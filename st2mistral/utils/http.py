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
import requests
import retrying

from oslo_config import cfg
from oslo_log import log as logging


LOG = logging.getLogger(__name__)


def retry_on_exceptions(exc):
    if isinstance(exc, requests.exceptions.ConnectionError):
        LOG.warning(
            '[stackstorm] HTTP request returned connection error. '
            'Retrying...'
        )

        return True
    else:
        LOG.error(
            '[stackstorm] HTTP request returned unexpected error. %s' %
            str(exc.message)
        )

        return False


@retrying.retry(
    retry_on_exception=retry_on_exceptions,
    wait_exponential_multiplier=cfg.CONF.st2.retry_exp_msec,
    wait_exponential_max=cfg.CONF.st2.retry_exp_max_msec,
    stop_max_delay=cfg.CONF.st2.retry_stop_max_msec)
def get(url, params=None, headers=None, token=None):
    if params and not isinstance(params, dict):
        raise TypeError('The params arg must be typeof dict.')

    headers = copy.deepcopy(headers) if headers else {}

    if token:
        headers['X-Auth-Token'] = str(token)

    return requests.get(url, params=params, headers=headers, verify=False)


@retrying.retry(
    retry_on_exception=retry_on_exceptions,
    wait_exponential_multiplier=cfg.CONF.st2.retry_exp_msec,
    wait_exponential_max=cfg.CONF.st2.retry_exp_max_msec,
    stop_max_delay=cfg.CONF.st2.retry_stop_max_msec)
def post(url, data, headers=None, token=None):
    headers = copy.deepcopy(headers) if headers else {}
    headers['Content-Type'] = 'application/json'

    if token:
        headers['X-Auth-Token'] = str(token)

    return requests.post(url, json.dumps(data), headers=headers, verify=False)


@retrying.retry(
    retry_on_exception=retry_on_exceptions,
    wait_exponential_multiplier=cfg.CONF.st2.retry_exp_msec,
    wait_exponential_max=cfg.CONF.st2.retry_exp_max_msec,
    stop_max_delay=cfg.CONF.st2.retry_stop_max_msec)
def put(url, data, headers=None, token=None):
    headers = copy.deepcopy(headers) if headers else {}
    headers['Content-Type'] = 'application/json'

    if token:
        headers['X-Auth-Token'] = str(token)

    return requests.put(url, json.dumps(data), headers=headers, verify=False)
