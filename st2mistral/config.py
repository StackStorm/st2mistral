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
        'auth_token',
        help='Auth token for st2 API.'
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
    cfg.CONF.import_opt('host', 'mistral.config', group='api')
    cfg.CONF.import_opt('port', 'mistral.config', group='api')
    cfg.CONF.register_opts(st2_opts, group='st2')
