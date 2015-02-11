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

import json
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

DATE_FORMAT_STRING = '%Y-%m-%dT%H:%M:%S.000000Z'


def _get_execution(execution_id, version='v2'):
    methods = {'v1': db_v1_api.execution_get, 'v2': db_v2_api.get_execution}
    try:
        return methods[version](execution_id)
    except exc.NotFoundException:
        return None


def _get_st2_context_from_db(action_context):

    exec_id = str(action_context['execution_id'])
    exec_db = _get_execution(exec_id, 'v2') or _get_execution(exec_id, 'v1')

    context = {}

    if isinstance(exec_db, db_v1_models.WorkflowExecution):
        context = {
            'parent': exec_db.context.get('st2_parent'),
            'endpoint': exec_db.context.get('st2_api_url'),
            'auth_token': exec_db.context.get('st2_auth_token')
        }
    elif isinstance(exec_db, db_v2_models.Execution):
        context = {
            'parent': exec_db.start_params.get('st2_parent'),
            'endpoint': exec_db.start_params.get('st2_api_url'),
            'auth_token': exec_db.start_params.get('st2_auth_token')
        }

    for k, v in six.iteritems(context):
        if isinstance(v, basestring):
            context[k] = str(v)

    return context


def _build_callback_url(action_context, version='v2'):
    if version == 'v1':
        return ('http://%s:%s/v1/workbooks/%s/executions/%s/tasks/%s' % (
                cfg.CONF.api.host, cfg.CONF.api.port,
                str(action_context.get('workbook_name')),
                str(action_context.get('execution_id')),
                str(action_context.get('task_id'))))
    elif version == 'v2':
        return ('http://%s:%s/v2/tasks/%s' % (
                cfg.CONF.api.host, cfg.CONF.api.port,
                str(action_context.get('task_id'))))
    else:
        return None


class St2Action(std_actions.HTTPAction):

    def __init__(self, action_context, ref, parameters=None, st2_context=None):

        # Get the context from the database for backward compatibility.
        if not st2_context:
            st2_context = _get_st2_context_from_db(action_context)

        if not st2_context or not st2_context.get('endpoint'):
            raise Exception('Invalid st2 context in the execution request.')

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

        if parameters:
            body['parameters'] = parameters

        super(St2Action, self).__init__(
            st2_context.get('endpoint'), method='POST',
            body=body, headers=headers)

    def is_sync(self):
        return False
