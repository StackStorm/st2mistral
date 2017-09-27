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

from yaql.language import factory
YAQL_ENGINE = factory.YaqlFactory().create()


class JinjaDataTestCase(base.JinjaFunctionTestCase):

    def test_function_from_json_string(self):
        obj = {'a': 'b', 'c': {'d': 'e', 'f': 1, 'g': True}}
        obj_json_str = json.dumps(obj)
        template = '{{ from_json_string(_.k1) }}'
        obj_str = self.eval_expression(template, {"k1": obj_json_str})
        actual_obj = eval(obj_str)
        self.assertDictEqual(obj, actual_obj)

    def test_function_from_yaml_string(self):
        obj = {'a': 'b', 'c': {'d': 'e', 'f': 1, 'g': True}}
        obj_yaml_str = yaml.safe_dump(obj)
        template = '{{ from_yaml_string(_.k1) }}'
        obj_str = self.eval_expression(template, {"k1": obj_yaml_str})
        actual_obj = eval(obj_str)
        self.assertDictEqual(obj, actual_obj)

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


class YAQLDataTestCase(base.YaqlFunctionTestCase):

    def test_function_from_json_string(self):
        obj = {'a': 'b', 'c': {'d': 'e', 'f': 1, 'g': True}}
        obj_json_str = json.dumps(obj)
        result = YAQL_ENGINE('from_json_string($.k1)').evaluate(
            context=self.get_yaql_context({'k1': obj_json_str})
        )
        actual_obj = eval(result)
        self.assertDictEqual(obj, actual_obj)

    def test_function_from_yaml_string(self):
        obj = {'a': 'b', 'c': {'d': 'e', 'f': 1, 'g': True}}
        obj_yaml_str = yaml.safe_dump(obj)
        result = YAQL_ENGINE('from_yaml_string($.k1)').evaluate(
            context=self.get_yaql_context({'k1': obj_yaml_str})
        )
        actual_obj = eval(result)
        self.assertDictEqual(obj, actual_obj)

    def test_to_complex(self):
        obj = {'a': 'b', 'c': {'d': 'e', 'f': 1, 'g': True}}
        result = YAQL_ENGINE('to_complex($.k1)').evaluate(
            context=self.get_yaql_context({'k1': obj})
        )
        actual_obj = json.loads(result)
        self.assertDictEqual(obj, actual_obj)

    def test_function_to_json_string(self):
        obj = {'a': 'b', 'c': {'d': 'e', 'f': 1, 'g': True}}
        result = YAQL_ENGINE('to_json_string($.k1)').evaluate(
            context=self.get_yaql_context({'k1': obj})
        )
        actual_obj = json.loads(result)
        self.assertDictEqual(obj, actual_obj)

    def test_function_to_yaml_string(self):
        obj = {'a': 'b', 'c': {'d': 'e', 'f': 1, 'g': True}}
        result = YAQL_ENGINE('to_yaml_string($.k1)').evaluate(
            context=self.get_yaql_context({'k1': obj})
        )
        actual_obj = yaml.load(result)
        self.assertDictEqual(obj, actual_obj)
