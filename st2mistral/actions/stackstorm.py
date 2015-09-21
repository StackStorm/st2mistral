# Copyright 2014 - StackStorm, Inc.
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

from oslo_config import cfg
from oslo_log import log as logging

from mistral.db.v2 import api as db_v2_api
from mistral import exceptions as exc
from mistral.actions import std_actions


LOG = logging.getLogger(__name__)


cfg.CONF.import_opt('host', 'mistral.config', group='api')
cfg.CONF.import_opt('port', 'mistral.config', group='api')
st2_opts = [cfg.StrOpt('auth_token', help='Auth token for st2 API.')]
cfg.CONF.register_opts(st2_opts, group='st2')


STATUS_MAP = {
    'RUNNING': 'running',
    'SUCCESS': 'succeeded',
    'ERROR': 'failed'
}

DATE_FORMAT_STRING = '%Y-%m-%dT%H:%M:%S.000000Z'


def _get_execution(execution_id, version='v2'):
    methods = {
        'v2': db_v2_api.get_execution
    }

    try:
        return methods[version](execution_id)
    except exc.NotFoundException:
        return None


def _build_callback_url(action_context, version='v2'):
    if version == 'v2':
        return ('http://%s:%s/v2/action_executions/%s' % (
                cfg.CONF.api.host, cfg.CONF.api.port,
                str(action_context.get('action_execution_id'))))
    else:
        return None


class St2Action(std_actions.HTTPAction):

    def __init__(self, action_context, ref, parameters=None, st2_context=None):
        if not st2_context or not st2_context.get('endpoint'):
            raise Exception('Invalid st2 context in the execution request.')

        endpoint = st2_context['endpoint']
        notify = st2_context.get('notify', {})
        skip_notify_tasks = st2_context.get('skip_notify_tasks', [])

        task_name = action_context.get('task_name', 'unknown')

        st2_action_context = {
            'parent': st2_context.get('parent'),
            'mistral': action_context
        }

        headers = {
            'content-type': 'application/json',
            'st2-context': json.dumps(st2_action_context)
        }

        if 'auth_token' in st2_context:
            headers['X-Auth-Token'] = st2_context.get('auth_token')
        elif 'st2' in cfg.CONF and 'auth_token' in cfg.CONF.st2:
            headers['X-Auth-Token'] = cfg.CONF.st2.auth_token

        callback = {
            'source': 'mistral',
            'url': _build_callback_url(action_context)
        }

        body = {
            'action': ref,
            'callback': callback
        }

        if task_name not in skip_notify_tasks:
            # We only include notifications settings if the task is not to be skipped
            body['notify'] = notify

        if parameters:
            body['parameters'] = parameters

        super(St2Action, self).__init__(url=endpoint, method='POST', body=body,
                                        headers=headers, verify=False)

    def is_sync(self):
        return False
