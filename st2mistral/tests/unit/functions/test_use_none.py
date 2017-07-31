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


class JinjaUseNoneTestCase(base.JinjaFunctionTestCase):

    def test_use_none(self):
        template = '{{ use_none(_.test_var) }}'
        actual = self.eval_expression(template, {'test_var': None})
        self.assertEqual(actual, '%*****__%NONE%__*****%')

        template = '{{ use_none(_.test_var) }}'
        actual = self.eval_expression(template, {'test_var': 'foobar'})
        self.assertEqual(actual, 'foobar')


class YAQLUseNoneTestCase(base.YaqlFunctionTestCase):

    def test_use_none(self):
        result = YAQL_ENGINE('use_none($.input_str)').evaluate(
            context=self.get_yaql_context({"input_str": None})
        )
        self.assertEqual(result, '%*****__%NONE%__*****%')

        result = YAQL_ENGINE('use_none($.input_str)').evaluate(
            context=self.get_yaql_context({"input_str": "foobar"})
        )
        self.assertEqual(result, 'foobar')
