# -*- coding: utf-8 -*-
#
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

import six
from oslo.config import cfg

from mistral.db.v1 import api as db_v1_api
from mistral.db.v2 import api as db_v2_api
from mistral.db.v1.sqlalchemy import models as db_v1_models
from mistral.db.v2.sqlalchemy import models as db_v2_models
from mistral import exceptions as exc
from mistral.actions import std_actions
from mistral.openstack.common import log as logging


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


def _get_execution(execution_id, version='v1'):
    methods = {'v1': db_v1_api.execution_get, 'v2': db_v2_api.get_execution}
    try:
        return methods[version](execution_id)
    except exc.NotFoundException:
        return None


def _get_st2_context(exec_db):
    context = {}

    if isinstance(exec_db, db_v1_models.WorkflowExecution):
        context = {
            'st2_parent': exec_db.context.get('st2_parent'),
            'st2_api_url': exec_db.context.get('st2_api_url'),
            'st2_auth_token': exec_db.context.get('st2_auth_token')
        }
    elif isinstance(exec_db, db_v2_models.Execution):
        context = {
            'st2_parent': exec_db.start_params.get('st2_parent'),
            'st2_api_url': exec_db.start_params.get('st2_api_url'),
            'st2_auth_token': exec_db.start_params.get('st2_auth_token')
        }

    for k, v in six.iteritems(context):
        if isinstance(v, basestring):
            context[k] = str(v)

    return context


def _build_callback_url(action_context, exec_db):
    if isinstance(exec_db, db_v1_models.WorkflowExecution):
        return ('http://%s:%s/v1/workbooks/%s/executions/%s/tasks/%s' % (
                cfg.CONF.api.host, cfg.CONF.api.port,
                str(action_context.get('workbook_name')),
                str(action_context.get('execution_id')),
                str(action_context.get('task_id'))))
    elif isinstance(exec_db, db_v2_models.Execution):
        return ('http://%s:%s/v2/tasks/%s' % (
                cfg.CONF.api.host, cfg.CONF.api.port,
                str(action_context.get('task_id'))))
    else:
        return None


class St2Action(std_actions.HTTPAction):

    def __init__(self, action_context, name, parameters=None):

        exec_id = str(action_context['execution_id'])
        exec_db = _get_execution(exec_id, 'v2') or _get_execution(exec_id, 'v1')
        st2_context = _get_st2_context(exec_db)

        headers = {
            'content-type': 'application/json',
            'st2-context': {'parent': st2_context.get('st2_parent')}
        }

        if 'st2_auth_token' in st2_context:
            headers['X-Auth-Token'] = st2_context.get('st2_auth_token')
        elif 'st2' in cfg.CONF and 'auth_token' in cfg.CONF.st2:
            headers['X-Auth-Token'] = cfg.CONF.st2.auth_token

        callback = {
            'source': 'mistral',
            'url': _build_callback_url(action_context, exec_db)
        }

        body = {
            'action': name,
            'parameters': parameters,
            'callback': callback
        }

        super(St2Action, self).__init__(
            st2_context.get('st2_api_url'), method='POST',
            body=body, headers=headers)

    def is_sync(self):
        return False


class St2Callback(std_actions.HTTPAction):

    def __init__(self, action_context, state, result):

        exec_id = str(action_context['execution_id'])
        exec_db = _get_execution(exec_id, 'v2') or _get_execution(exec_id, 'v1')
        st2_context = _get_st2_context(exec_db)

        headers = {'content-type': 'application/json'}

        if 'st2_auth_token' in st2_context:
            headers['X-Auth-Token'] = st2_context.get('st2_auth_token')
        elif 'st2' in cfg.CONF and 'auth_token' in cfg.CONF.st2:
            headers['X-Auth-Token'] = cfg.CONF.st2.auth_token

        body = {
            'action': str(action_context.get('workflow_name')),
            'status': STATUS_MAP[state],
            'result': {
                'id': str(action_context.get('execution_id')),
                'state': state,
                'output': result
            }
        }

        super(St2Callback, self).__init__(
            '%s/%s' % (st2_context.get('st2_api_url'),
                       st2_context.get('st2_parent')),
            method='PUT', body=body, headers=headers)
