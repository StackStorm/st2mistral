# Copyright 2014 - StackStorm, Inc.
# Copyright 2016 - Brocade Communications Systems, Inc.
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

import copy
import json

from oslo_config import cfg
from oslo_log import log as logging

from st2mistral import config
config.register_opts()

from mistral.actions import base
from mistral.db.v2 import api as db_v2_api
from mistral import exceptions as exc
from mistral.workflow import utils as wf_utils

from st2mistral.utils import http


LOG = logging.getLogger(__name__)


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


class St2Action(base.Action):

    def __init__(self, action_context, ref, parameters=None, st2_context=None):
        if not st2_context or not st2_context.get('api_url'):
            raise exc.ActionException(
                'Failed to initialize %s [action_context=%s, '
                'ref=%s]: Invalid st2 context.' % (
                    self.__class__.__name__, action_context, ref
                )
            )

        self.action_context = action_context
        self.ref = ref
        self.parameters = parameters
        self.st2_context = st2_context
        self.st2_context_log_safe = copy.deepcopy(st2_context)
        self.st2_context_log_safe.pop('auth_token', None)

    def run(self):
        LOG.info(
            'Running %s [action_context=%s, ref=%s, '
            'parameters=%s, st2_context=%s]' % (
                self.__class__.__name__, self.action_context, self.ref,
                self.parameters, self.st2_context_log_safe
            )
        )

        endpoint = self.st2_context['api_url'] + '/actionexecutions'

        st2_action_context = {
            'parent': self.st2_context.get('parent'),
            'mistral': self.action_context
        }

        headers = {
            'st2-context': json.dumps(st2_action_context)
        }

        token = None

        if 'auth_token' in self.st2_context:
            token = self.st2_context.get('auth_token')

        body = {
            'action': self.ref,
            'callback': {
                'source': 'mistral_v2',
                'url': _build_callback_url(self.action_context)
            }
        }

        notify = self.st2_context.get('notify', {})
        skip_notify_tasks = self.st2_context.get('skip_notify_tasks', [])
        task_name = self.action_context.get('task_name', 'unknown')

        # Include notifications settings if the task is not to be skipped.
        if task_name not in skip_notify_tasks:
            body['notify'] = notify

        if self.parameters:
            body['parameters'] = self.parameters

        LOG.info(
            'Sending HTTP request for %s [action_context=%s, '
            'ref=%s, parameters=%s, st2_context=%s]' % (
                self.__class__.__name__, self.action_context, self.ref,
                self.parameters, self.st2_context_log_safe
            )
        )

        try:
            resp = http.post(endpoint, body, headers=headers, token=token)
        except Exception as e:
            raise exc.ActionException(
                'Failed to send HTTP request for %s [action_context=%s, '
                'ref=%s, parameters=%s, st2_context=%s]: %s' % (
                    self.__class__.__name__, self.action_context, self.ref,
                    self.parameters, self.st2_context_log_safe, e
                )
            )

        LOG.info(
            'Received HTTP response for %s [action_context=%s, '
            'ref=%s, parameters=%s, st2_context=%s]:\n%s\n%s' % (
                self.__class__.__name__, self.action_context, self.ref,
                self.parameters, self.st2_context_log_safe,
                resp.status_code, resp.content
            )
        )

        try:
            content = resp.json()
        except Exception as e:
            content = resp.content

        result = {
            'content': content,
            'status': resp.status_code,
            'headers': dict(resp.headers.items()),
            'url': resp.url,
            'history': resp.history,
            'encoding': resp.encoding,
            'reason': resp.reason,
            'cookies': dict(resp.cookies.items()),
            'elapsed': resp.elapsed.total_seconds()
        }

        if resp.status_code not in range(200, 307):
            return wf_utils.Result(error=result)

        return result

    def is_sync(self):
        return False

    def test(self):
        return None
