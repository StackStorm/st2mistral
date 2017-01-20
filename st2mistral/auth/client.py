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

import os

import mistralclient.api.httpclient as api
from mistralclient import auth


class St2AuthHandler(auth.AuthHandler):

    def authenticate(self, req):
        """Pass the authentication to server for handling.

        This is a plugin to be used in mistralclient. The credential will
        not be processed in mistralclient. It will be passed to the mistral
        server for validation. If auth token is not provided in the request,
        the plugin will look for the ST2_AUTH_TOKEN in the environment
        variables.

        :param req: Request dict containing list of parameters required
            for server side authentication.

        """
        if not isinstance(req, dict):
            raise TypeError('The input "req" is not typeof dict.')

        auth_token = req.get('auth_token')

        if not auth_token:
            auth_token = os.environ.get('ST2_AUTH_TOKEN')

        auth_response = {
            'mistral_url': req.get('mistral_url'),
            api.AUTH_TOKEN: auth_token,
            api.CACERT: req.get('cacert'),
            api.INSECURE: req.get('insecure')
        }

        return auth_response
