# Copyright 2017 - Brocade Communications Systems, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import json
import six
from six.moves import http_client

from oslo_log import log as logging

from st2mistral import config
config.register_opts()

from mistral.db.v2 import api as db_api
from mistral.notifiers import base
from mistral.notifiers import notification_events as events
from mistral.workflow import states

from st2mistral.utils import http


LOG = logging.getLogger(__name__)


WF_EX_STATUS_MAP = {
    states.RUNNING: 'running',
    states.SUCCESS: 'succeeded',
    states.CANCELLED: 'canceled',
    states.ERROR: 'failed',
    states.PAUSED: 'paused'
}


def get_st2_ctx(data):
    return data['params']['env']['__actions']['st2.action']['st2_context']


def try_json_loads(s):
    try:
        return json.loads(s) if s and isinstance(s, six.string_types) else s
    except Exception:
        return s


def on_workflow_status_update(ex_id, data, event, timestamp, **kwargs):
    root_id = data.get('root_execution_id') or ex_id

    if root_id != ex_id:
        LOG.info(
            '[%s] The workflow event %s for subworkflow %s is '
            'not published to st2. This is expected because it '
            'does not have a corresponding execution record in st2.',
            root_id,
            event,
            ex_id
        )

        return

    wf_ex_env = data['params']['env']
    st2_ex_id = wf_ex_env['st2_execution_id']
    st2_ctx = wf_ex_env['__actions']['st2.action']['st2_context']
    st2_token = st2_ctx.get('auth_token')
    endpoint = st2_ctx['api_url'] + '/executions/' + st2_ex_id

    body = {
        'status': WF_EX_STATUS_MAP[data['state']],
        'result': data.get('output', {})
    }

    body['result']['extra'] = {
        'state': data['state'],
        'state_info': data['state_info']
    }

    # If workflow is in completed state, then
    # include task details in the result.
    if states.is_paused_or_completed(data['state']):
        with db_api.transaction():
            wf_ex = db_api.get_workflow_execution(ex_id)
            task_exs = [
                task_ex.to_dict()
                for task_ex in wf_ex.task_executions
            ]

        if task_exs:
            body['result']['tasks'] = []

            for task_ex in task_exs:
                task_result = {
                    'id': task_ex['id'],
                    'name': task_ex['name'],
                    'workflow_execution_id': task_ex.get(
                        'workflow_execution_id',
                        None
                    ),
                    'workflow_name': task_ex['workflow_name'],
                    'created_at': task_ex.get('created_at', None),
                    'updated_at': task_ex.get('updated_at', None),
                    'state': task_ex.get('state', None),
                    'state_info': task_ex.get('state_info', None),
                    'input': try_json_loads(task_ex.get('input', None)),
                    'published': try_json_loads(
                        task_ex.get('published', None)
                    ),
                    'result': try_json_loads(task_ex.get('result', None))
                }

                body['result']['tasks'].append(task_result)

    LOG.info(
        '[%s] The workflow event %s for %s will be published to st2.',
        root_id,
        event,
        ex_id
    )

    resp = http.put(endpoint, body, token=st2_token)

    if resp.status_code == http_client.OK:
        LOG.info(
            '[%s] The workflow event %s for %s is published to st2.',
            root_id,
            event,
            ex_id
        )
    else:
        raise Exception(
            '[%s] Unable to publish event because st2 returned '
            'status code %s. %s' % (root_id, resp.status_code, resp.text)
        )


def trigger_workflow_event(
        root_id, task_ex_id, task_event,
        wf_event, wf_ex_data, timestamp, **kwargs):

    LOG.info(
        '[%s] The task event %s for %s triggers '
        'workflow event %s for %s to st2.',
        root_id,
        task_event,
        task_ex_id,
        wf_event,
        wf_ex_data['id']
    )

    on_workflow_status_update(
        wf_ex_data['id'],
        wf_ex_data,
        wf_event,
        timestamp,
        **kwargs
    )


def on_task_status_update(ex_id, data, event, timestamp, **kwargs):
    with db_api.transaction():
        task_ex = db_api.load_task_execution(ex_id)
        wf_ex = task_ex.workflow_execution
        wf_ex_data = wf_ex.to_dict()
        parent_wf_tk_id = wf_ex.task_execution_id

    root_id = wf_ex_data.get('root_execution_id') or wf_ex_data.get('id')

    LOG.info(
        '[%s] The task event %s for %s will be processed for st2.',
        root_id,
        event,
        ex_id
    )

    if wf_ex_data['state'] == states.CANCELLED:
        trigger_workflow_event(
            root_id,
            ex_id,
            event,
            events.WORKFLOW_CANCELLED,
            wf_ex_data,
            timestamp,
            **kwargs
        )

    if wf_ex_data['state'] == states.PAUSED:
        trigger_workflow_event(
            root_id,
            ex_id,
            event,
            events.WORKFLOW_PAUSED,
            wf_ex_data,
            timestamp,
            **kwargs
        )

        # Cascade event upstream (from workbook subworkflow).
        while parent_wf_tk_id:
            with db_api.transaction():
                parent_wf_tk_ex = db_api.get_task_execution(parent_wf_tk_id)
                parent_wf_ex = parent_wf_tk_ex.workflow_execution
                parent_wf_ex_data = parent_wf_ex.to_dict()
                grant_parent_wf_tk_id = parent_wf_ex.task_execution_id

            if parent_wf_ex_data['state'] != states.PAUSED:
                break

            trigger_workflow_event(
                root_id,
                ex_id,
                event,
                events.WORKFLOW_PAUSED,
                parent_wf_ex_data,
                timestamp,
                **kwargs
            )

            parent_wf_tk_id = grant_parent_wf_tk_id

        # Cascade event upstream (from subworkflow action).
        st2_ctx = get_st2_ctx(wf_ex_data)
        parent_ctx = st2_ctx.get('parent', {}).get('mistral', {})
        parent_wf_ex_id = parent_ctx.get('workflow_execution_id')

        while parent_wf_ex_id:
            with db_api.transaction():
                parent_wf_ex = db_api.get_workflow_execution(parent_wf_ex_id)
                parent_wf_ex_data = parent_wf_ex.to_dict()

            if parent_wf_ex_data['state'] != states.PAUSED:
                break

            trigger_workflow_event(
                root_id,
                ex_id,
                event,
                events.WORKFLOW_PAUSED,
                parent_wf_ex_data,
                timestamp,
                **kwargs
            )

            st2_ctx = get_st2_ctx(parent_wf_ex_data)
            parent_ctx = st2_ctx.get('parent', {}).get('mistral', {})
            parent_wf_ex_id = parent_ctx.get('workflow_execution_id')

    LOG.info(
        '[%s] The task event %s for %s is processed for st2.',
        root_id,
        event,
        ex_id
    )


EVENT_FUNCTION_MAP = {
    events.WORKFLOW_LAUNCHED: on_workflow_status_update,
    events.WORKFLOW_SUCCEEDED: on_workflow_status_update,
    events.WORKFLOW_FAILED: on_workflow_status_update,
    events.WORKFLOW_CANCELLED: on_workflow_status_update,
    events.WORKFLOW_PAUSED: on_workflow_status_update,
    events.WORKFLOW_RESUMED: on_workflow_status_update,
    events.TASK_SUCCEEDED: on_task_status_update,
    events.TASK_FAILED: on_task_status_update,
    events.TASK_CANCELLED: on_task_status_update,
    events.TASK_PAUSED: on_task_status_update
}


class St2Notifier(base.NotificationPublisher):

    def publish(self, ex_id, data, event, timestamp, **kwargs):
        func = EVENT_FUNCTION_MAP.get(event)

        if not func:
            LOG.info(
                'The event %s for %s is not processed for st2 '
                'because there is no event handler defined.',
                event,
                ex_id
            )

            return

        func(ex_id, data, event, timestamp, **kwargs)
