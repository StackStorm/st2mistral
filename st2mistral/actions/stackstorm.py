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

import copy
import json

import requests
import retrying
from oslo_config import cfg
from oslo_log import log as logging

from mistral.db.v2 import api as db_v2_api
from mistral import exceptions as exc
from mistral.actions import base
from mistral.workflow import utils as wf_utils


LOG = logging.getLogger(__name__)


cfg.CONF.import_opt('host', 'mistral.config', group='api')
cfg.CONF.import_opt('port', 'mistral.config', group='api')

st2_opts = [
    cfg.StrOpt('auth_token', help='Auth token for st2 API.'),
    cfg.IntOpt('retry_exp_msec', default=1000, help='Multiplier for the exponential backoff.'),
    cfg.IntOpt('retry_exp_max_msec', default=60000, help='Max time for each set of backoff.'),
    cfg.IntOpt('retry_stop_max_msec', default=180000, help='Max time to stop retrying.'),
]

cfg.CONF.register_opts(st2_opts, group='st2')


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


def _retry_on_exceptions(exc):
    LOG.warning('St2Action failed with exception type %s. Determining '
                'if action execution can be retried...', type(exc))

    is_connection_error = isinstance(exc, requests.exceptions.ConnectionError)

    return is_connection_error


class St2Action(base.Action):

    def __init__(self, action_context, ref, parameters=None, st2_context=None):
        if not st2_context or not st2_context.get('endpoint'):
            raise exc.ActionException(
                'Failed to initialize %s [action_context=%s, '
                'ref=%s]: Invalid st2 context.' % (
                self.__class__.__name__, action_context, ref)
            )

        self.action_context = action_context
        self.ref = ref
        self.parameters = parameters
        self.st2_context = st2_context
        self.st2_context_log_safe = copy.deepcopy(st2_context)
        self.st2_context_log_safe.pop('auth_token', None)

    @retrying.retry(
        retry_on_exception=_retry_on_exceptions,
        wait_exponential_multiplier=cfg.CONF.st2.retry_exp_msec,
        wait_exponential_max=cfg.CONF.st2.retry_exp_max_msec,
        stop_max_delay=cfg.CONF.st2.retry_stop_max_msec)
    def request(self, method, endpoint, headers, data, verify=False):
        LOG.info('Sending HTTP request for %s [action_context=%s, '
                 'ref=%s, parameters=%s, st2_context=%s]' % (
                 self.__class__.__name__, self.action_context, self.ref,
                 self.parameters, self.st2_context_log_safe))

        return requests.request(
            method,
            endpoint,
            data=data,
            headers=headers,
            verify=verify
        )

    def run(self):
        LOG.info('Running %s [action_context=%s, ref=%s, '
                 'parameters=%s, st2_context=%s]' % (
                 self.__class__.__name__, self.action_context, self.ref,
                 self.parameters, self.st2_context_log_safe))

        method = 'POST'
        endpoint = self.st2_context['endpoint']

        st2_action_context = {
            'parent': self.st2_context.get('parent'),
            'mistral': self.action_context
        }

        headers = {
            'content-type': 'application/json',
            'st2-context': json.dumps(st2_action_context)
        }

        if 'auth_token' in self.st2_context:
            headers['X-Auth-Token'] = self.st2_context.get('auth_token')
        elif 'st2' in cfg.CONF and 'auth_token' in cfg.CONF.st2:
            headers['X-Auth-Token'] = cfg.CONF.st2.auth_token

        body = {
            'action': self.ref,
            'callback': {
                'source': 'mistral',
                'url': _build_callback_url(self.action_context)
            }
        }

        notify = self.st2_context.get('notify', {})
        skip_notify_tasks = self.st2_context.get('skip_notify_tasks', [])
        task_name = self.action_context.get('task_name', 'unknown')

        if task_name not in skip_notify_tasks:
            # We only include notifications settings if the task is not to be skipped
            body['notify'] = notify

        if self.parameters:
            body['parameters'] = self.parameters

        data = json.dumps(body) if isinstance(body, dict) else body

        try:
            resp = self.request(method, endpoint, headers, data)
        except Exception as e:
            raise exc.ActionException(
                'Failed to send HTTP request for %s [action_context=%s, '
                'ref=%s, parameters=%s, st2_context=%s]: %s' % (
                self.__class__.__name__, self.action_context, self.ref,
                self.parameters, self.st2_context_log_safe, e)
            )

        LOG.info('Received HTTP response for %s [action_context=%s, '
                 'ref=%s, parameters=%s, st2_context=%s]:\n%s\n%s' % (
                 self.__class__.__name__, self.action_context, self.ref,
                 self.parameters, self.st2_context_log_safe,
                 resp.status_code, resp.content))

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
