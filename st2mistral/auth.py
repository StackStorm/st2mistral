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

import requests
from six.moves import http_client

from oslo_config import cfg
from oslo_log import log as logging

from mistral import auth
from mistral import exceptions as exc

from st2mistral.utils import http


LOG = logging.getLogger(__name__)


class St2AuthHandler(auth.AuthHandler):

    def authenticate(self, req):
        token = req.headers.get('X-Auth-Token')

        if not token:
            raise exc.UnauthorizedException('Auth token is not provided.')

        data = {'token': token}
        headers = {'St2-Api-Key': cfg.CONF.st2.api_key}
        url = cfg.CONF.st2.auth_url + '/tokens/validate'
        resp = http.post(url, data, headers=headers)

        if resp.status_code != http_client.OK or not resp.json().get('valid', False):
            LOG.error('Unable to verify auth token. %s' % str(resp.content))
            raise exc.UnauthorizedException('Unable to verify auth token.')
