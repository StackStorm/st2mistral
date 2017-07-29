# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import yaml

from st2mistral.tests.unit import test_function_base as base


class JinjaUtilsDataFunctionTestCase(base.JinjaFunctionTestCase):

    def test_function_to_complex(self):
        obj = {'a': 'b', 'c': {'d': 'e', 'f': 1, 'g': True}}
        template = '{{ to_complex(_.k1) }}'
        obj_json_str = self.eval_expression(template, {"k1": obj})
        actual_obj = json.loads(obj_json_str)
        self.assertDictEqual(obj, actual_obj)

    def test_function_to_json_string(self):
        obj = {'a': 'b', 'c': {'d': 'e', 'f': 1, 'g': True}}
        template = '{{ to_json_string(_.k1) }}'
        obj_json_str = self.eval_expression(template, {"k1": obj})
        actual_obj = json.loads(obj_json_str)
        self.assertDictEqual(obj, actual_obj)

    def test_function_to_yaml_string(self):
        obj = {'a': 'b', 'c': {'d': 'e', 'f': 1, 'g': True}}
        template = '{{ to_yaml_string(_.k1) }}'
        obj_yaml_str = self.eval_expression(template, {"k1": obj})
        actual_obj = yaml.load(obj_yaml_str)
        self.assertDictEqual(obj, actual_obj)
