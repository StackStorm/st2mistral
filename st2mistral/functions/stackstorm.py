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

from mistral import exceptions as exc
from st2common.jinja.filters import crypto
from st2common.jinja.filters import data
from st2common.jinja.filters import regex
from st2common.jinja.filters import complex_type
from st2common.jinja.filters import time
from st2common.jinja.filters import version
from st2common.jinja.filters import json_escape
from st2common.util.jinja import use_none
from st2mistral.utils import http

from st2mistral import config
config.register_opts()


LOG = logging.getLogger(__name__)


def decrypt_kv_(*args, **kwargs):
    return crypto.decrypt_kv(*args, **kwargs)


def to_json_string_(*args, **kwargs):
    return data.to_json_string(*args, **kwargs)


def to_yaml_string_(*args, **kwargs):
    return data.to_yaml_string(*args, **kwargs)


def to_complex_(*args, **kwargs):
    return complex_type.to_complex(*args, **kwargs)


def regex_match_(*args, **kwargs):
    return regex.regex_match(*args, **kwargs)


def regex_replace_(*args, **kwargs):
    return regex.regex_replace(*args, **kwargs)


def regex_search_(*args, **kwargs):
    return regex.regex_search(*args, **kwargs)


def regex_substring_(*args, **kwargs):
    return regex.regex_substring(*args, **kwargs)


def to_human_time_from_seconds_(*args, **kwargs):
    return time.to_human_time_from_seconds(*args, **kwargs)


def version_compare_(*args, **kwargs):
    return version.version_compare(*args, **kwargs)


def version_more_than_(*args, **kwargs):
    return version.version_more_than(*args, **kwargs)


def version_less_than_(*args, **kwargs):
    return version.version_less_than(*args, **kwargs)


def version_equal_(*args, **kwargs):
    return version.version_equal(*args, **kwargs)


def version_match_(*args, **kwargs):
    return version.version_match(*args, **kwargs)


def version_bump_major_(*args, **kwargs):
    return version.version_bump_major(*args, **kwargs)


def version_bump_minor_(*args, **kwargs):
    return version.version_bump_minor(*args, **kwargs)


def version_bump_patch_(*args, **kwargs):
    return version.version_bump_patch(*args, **kwargs)


def version_strip_patch_(*args, **kwargs):
    return version.version_strip_patch(*args, **kwargs)


def use_none_(*args, **kwargs):
    return json_escape.json_escape(*args, **kwargs)


def json_escape_(*args, **kwargs):
    return use_none(*args, **kwargs)


def st2kv_(context, key):

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
    params = {'decrypt': True, 'scope': scope}

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
