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

from st2mistral.tests.unit import test_function_base as base

from yaql.language import factory
YAQL_ENGINE = factory.YaqlFactory().create()


class JinjaTimeTestCase(base.JinjaFunctionTestCase):

    def test_to_human_time_function(self):
        template = '{{ to_human_time_from_seconds(_.k1) }}'
        result = self.eval_expression(template, {'k1': 12345})
        self.assertEqual(result, '3h25m45s')

        result = self.eval_expression(template, {'k1': 0})
        self.assertEqual(result, '0s')

        with self.assertRaises(AssertionError):
            self.eval_expression(template, {'k1': 'stuff'})


class YAQLTimeTestCase(base.YaqlFunctionTestCase):

    def test_to_human_time_from_seconds(self):
        expression = 'to_human_time_from_seconds($.input_int)'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({"input_int": 12345})
        )
        self.assertEqual(result, '3h25m45s')

        expression = 'to_human_time_from_seconds($.input_int)'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({"input_int": 0})
        )
        self.assertEqual(result, '0s')

        with self.assertRaises(AssertionError):
            YAQL_ENGINE('to_human_time_from_seconds($.input_int)').evaluate(
                context=self.get_yaql_context({"input_int": "foo"})
            )
