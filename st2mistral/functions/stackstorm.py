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
from six.moves import http_client

from oslo_config import cfg
from oslo_log import log as logging

from st2mistral import config
config.register_opts()

from mistral import exceptions as exc
from st2mistral.utils import http

LOG = logging.getLogger(__name__)


def st2kv_(context, key, decrypt=False):
    """Retrieve value for provided key in StackStorm datastore

    :param key: User to whom key belongs.
    :type key: ``str``
    :param decrypt: Request a decrypted version of the value (defaults to False)
    :type decrypt: ``bool``

    :rtype: ``dict``
    """

    # Get StackStorm auth token from the action context.
    token = None
    env = context['__env']
    actions_env = env.get('__actions', {})
    st2_ctx = actions_env.get('st2.action', {}).get('st2_context', {})
    st2_ctx_log_safe = copy.deepcopy(st2_ctx)
    st2_ctx_log_safe.pop('auth_token', None)

    if 'auth_token' in st2_ctx:
        token = st2_ctx.get('auth_token')
    elif 'st2' in cfg.CONF and 'auth_token' in cfg.CONF.st2:
        token = cfg.CONF.st2.auth_token

    if key.startswith('system.'):
        scope = 'system'
        key_id = key[key.index('.') + 1:]
    else:
        scope = 'user'
        key_id = key

    endpoint = st2_ctx['api_url'] + '/keys/' + key_id
    params = {'decrypt': decrypt, 'scope': scope}

    LOG.info(
        'Sending HTTP request for custom YAQL function st2kv '
        '[url=%s, st2_context=%s]' % (
            endpoint, st2_ctx_log_safe
        )
    )

    try:
        resp = http.get(endpoint, params=params, token=token)
    except Exception as e:
        raise exc.CustomYaqlException(
            'Failed to send HTTP request for custom YAQL function st2kv '
            '[url=%s, st2_context=%s]: %s' % (
                endpoint, st2_ctx_log_safe, e
            )
        )

    if resp.status_code == http_client.NOT_FOUND:
        raise exc.YaqlEvaluationException(
            'Key %s does not exist in StackStorm datastore.' % key
        )
    elif resp.status_code != http_client.OK:
        raise exc.YaqlEvaluationException(
            'Failed to send HTTP request for custom YAQL function st2kv '
            '[url=%s, st2_context=%s]: %s' % (
                endpoint, st2_ctx_log_safe, resp.text
            )
        )

    return resp.json().get('value', None)
