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

import jmespath

from st2mistral.tests.unit import test_function_base as base

from yaql.language import factory
YAQL_ENGINE = factory.YaqlFactory().create()


class JinjaDataTestCase(base.JinjaFunctionTestCase):

    def test_function_jmespath_query_static(self):
        obj = {'people': [{'first': 'James', 'last': 'd'},
                          {'first': 'Jacob', 'last': 'e'},
                          {'first': 'Jayden', 'last': 'f'},
                          {'missing': 'different'}],
               'foo': {'bar': 'baz'}}

        template = '{{ jmespath_query(_.obj, "people[*].first") }}'
        result = self.eval_expression(template, {"obj": obj})
        actual = eval(result)
        expected = ['James', 'Jacob', 'Jayden']
        self.assertEqual(actual, expected)

    def test_function_jmespath_query_dynamic(self):
        obj = {'people': [{'first': 'James', 'last': 'd'},
                          {'first': 'Jacob', 'last': 'e'},
                          {'first': 'Jayden', 'last': 'f'},
                          {'missing': 'different'}],
               'foo': {'bar': 'baz'}}
        query = "people[*].last"

        template = '{{ jmespath_query(_.obj, _.query) }}'
        result = self.eval_expression(template, {"obj": obj,
                                                 'query': query})
        actual = eval(result)
        expected = ['d', 'e', 'f']
        self.assertEqual(actual, expected)


class YAQLDataTestCase(base.YaqlFunctionTestCase):

    def test_function_jmespath_query_static(self):
        obj = {'people': [{'first': 'James', 'last': 'd'},
                          {'first': 'Jacob', 'last': 'e'},
                          {'first': 'Jayden', 'last': 'f'},
                          {'missing': 'different'}],
               'foo': {'bar': 'baz'}}
        result = YAQL_ENGINE('jmespath_query($.obj, "people[*].first")').evaluate(
            context=self.get_yaql_context({'obj': obj})
        )
        expected = ['James', 'Jacob', 'Jayden']
        self.assertEqual(result, expected)

    def test_function_jmespath_query_dynamic(self):
        obj = {'people': [{'first': 'James', 'last': 'd'},
                          {'first': 'Jacob', 'last': 'e'},
                          {'first': 'Jayden', 'last': 'f'},
                          {'missing': 'different'}],
               'foo': {'bar': 'baz'}}
        query = "people[*].last"
        result = YAQL_ENGINE('jmespath_query($.obj, $.query)').evaluate(
            context=self.get_yaql_context({'obj': obj,
                                           'query': query})
        )
        expected = ['d', 'e', 'f']
        self.assertEqual(result, expected)
