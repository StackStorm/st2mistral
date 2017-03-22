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

from six.moves import http_client

from oslo_config import cfg
from oslo_log import log as logging

from mistral import auth
from mistral import exceptions as exc

from st2mistral.utils import http


LOG = logging.getLogger(__name__)


class St2AuthHandler(auth.AuthHandler):

    def auth_with_apikey(self, req):
        apikey = req.headers.get('X-Auth-Token')

        if not apikey:
            LOG.error('X-Auth-Token is not in headers.')
            return False

        # The API call to validate the API key requires a different API key.
        headers = {'St2-Api-Key': cfg.CONF.st2.api_key}
        url = cfg.CONF.st2.api_url + '/v1/apikeys/' + apikey
        resp = http.get(url, headers=headers)

        authenticated = resp.status_code == http_client.OK

        if authenticated:
            LOG.info('Authenticated using API key.')
        else:
            LOG.warn('Unable to verify API key. %s' % str(resp.content))

        return authenticated

    def auth_with_token(self, req):
        token = req.headers.get('X-Auth-Token')

        if not token:
            LOG.error('X-Auth-Token is not in headers.')
            return False

        # The API call to validate the token requires a different API key.
        data = {'token': token}
        headers = {'St2-Api-Key': cfg.CONF.st2.api_key}
        url = cfg.CONF.st2.auth_url + '/tokens/validate'
        resp = http.post(url, data, headers=headers)

        authenticated = (resp.status_code == http_client.OK and
                         resp.json().get('valid', False))
       
        if authenticated: 
            LOG.info('Authenticated using auth token.')
        else:
            LOG.warn('Unable to verify auth token. %s' % str(resp.content))

        return authenticated

    def authenticate(self, req):
        authenticated = self.auth_with_apikey(req) or self.auth_with_token(req)

        if not authenticated:
            raise exc.UnauthorizedException('Unable to verify auth token.')
