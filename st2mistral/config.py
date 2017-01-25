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


from oslo_config import cfg
from oslo_log import log as logging


LOG = logging.getLogger(__name__)


st2_opts = [
    cfg.StrOpt(
        'auth_url',
        default='https://localhost/auth',
        help='Auth endpoint for st2.'
    ),
    cfg.StrOpt(
        'api_key',
        help='API key to authenticate with the auth '
             'endpoint for token validation.'
    ),
    cfg.IntOpt(
        'token_ttl_sec',
        default=300,
        help='The amount of time before cached auth token is expired.'
    ),
    cfg.IntOpt(
        'retry_exp_msec',
        default=1000,
        help='Multiplier for the exponential backoff.'
    ),
    cfg.IntOpt(
        'retry_exp_max_msec',
        default=60000,
        help='Max time for each set of backoff.'
    ),
    cfg.IntOpt(
        'retry_stop_max_msec',
        default=180000,
        help='Max time to stop retrying.'
    )
]


def register_opts():
    if 'api' not in cfg.CONF or 'host' in cfg.CONF.api:
        cfg.CONF.import_opt('host', 'mistral.config', group='api')

    if 'api' not in cfg.CONF or 'port' in cfg.CONF.api:
        cfg.CONF.import_opt('port', 'mistral.config', group='api')

    if 'st2' not in cfg.CONF:
        cfg.CONF.register_opts(st2_opts, group='st2')
