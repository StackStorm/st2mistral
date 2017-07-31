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


class JinjaVersionTestCase(base.JinjaFunctionTestCase):

    def test_version_compare(self):
        template = '{{ version_compare(_.version, "0.10.0") }}'
        result = self.eval_expression(template, {'version': '0.9.0'})
        self.assertEqual(result, '-1')

        template = '{{ version_compare(_.version, "0.10.0") }}'
        result = self.eval_expression(template, {'version': '0.10.1'})
        self.assertEqual(result, '1')

        template = '{{ version_compare(_.version, "0.10.0") }}'
        result = self.eval_expression(template, {'version': '0.10.0'})
        self.assertEqual(result, '0')

    def test_version_more_than(self):
        template = '{{ version_more_than(_.version, "0.10.0") }}'
        result = self.eval_expression(template, {'version': '0.9.0'})
        self.assertEqual(result, 'False')

        template = '{{ version_more_than(_.version, "0.10.0") }}'
        result = self.eval_expression(template, {'version': '0.10.1'})
        self.assertEqual(result, 'True')

        template = '{{ version_more_than(_.version, "0.10.0") }}'
        result = self.eval_expression(template, {'version': '0.10.0'})
        self.assertEqual(result, 'False')

    def test_version_less_than(self):
        template = '{{ version_less_than(_.version, "0.10.0") }}'
        result = self.eval_expression(template, {'version': '0.9.0'})
        self.assertEqual(result, 'True')

        template = '{{ version_less_than(_.version, "0.10.0") }}'
        result = self.eval_expression(template, {'version': '0.10.1'})
        self.assertEqual(result, 'False')

        template = '{{ version_less_than(_.version, "0.10.0") }}'
        result = self.eval_expression(template, {'version': '0.10.0'})
        self.assertEqual(result, 'False')

    def test_version_equal(self):
        template = '{{ version_equal(_.version, "0.10.0") }}'
        result = self.eval_expression(template, {'version': '0.9.0'})
        self.assertEqual(result, 'False')

        template = '{{ version_equal(_.version, "0.10.0") }}'
        result = self.eval_expression(template, {'version': '0.10.1'})
        self.assertEqual(result, 'False')

        template = '{{ version_equal(_.version, "0.10.0") }}'
        result = self.eval_expression(template, {'version': '0.10.0'})
        self.assertEqual(result, 'True')

    def test_version_match(self):
        template = '{{ version_match(_.version, ">0.10.0") }}'
        result = self.eval_expression(template, {'version': '0.10.1'})
        self.assertEqual(result, 'True')
        result = self.eval_expression(template, {'version': '0.1.1'})
        self.assertEqual(result, 'False')

        template = '{{ version_match(_.version, "<0.10.0") }}'
        result = self.eval_expression(template, {'version': '0.1.0'})
        self.assertEqual(result, 'True')
        result = self.eval_expression(template, {'version': '1.1.0'})
        self.assertEqual(result, 'False')

        template = '{{ version_match(_.version, "==0.10.0") }}'
        result = self.eval_expression(template, {'version': '0.10.0'})
        self.assertEqual(result, 'True')
        result = self.eval_expression(template, {'version': '0.10.1'})
        self.assertEqual(result, 'False')

    def test_version_bump_major(self):
        template = '{{ version_bump_major(_.version) }}'
        result = self.eval_expression(template, {'version': '0.10.1'})
        self.assertEqual(result, '1.0.0')

    def test_version_bump_minor(self):
        template = '{{ version_bump_minor(_.version) }}'
        result = self.eval_expression(template, {'version': '0.10.1'})
        self.assertEqual(result, '0.11.0')

    def test_version_bump_patch(self):
        template = '{{ version_bump_patch(_.version) }}'
        result = self.eval_expression(template, {'version': '0.10.1'})
        self.assertEqual(result, '0.10.2')

    def test_version_strip_patch(self):
        template = '{{ version_strip_patch(_.version) }}'
        result = self.eval_expression(template, {'version': '0.10.1'})
        self.assertEqual(result, '0.10')


class YAQLVersionTestCase(base.YaqlFunctionTestCase):

    def test_version_compare(self):
        expression = 'version_compare($.version, "0.10.0")'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.9.0'})
        )
        self.assertEqual(result, -1)

        expression = 'version_compare($.version, "0.10.0")'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, 1)

        expression = 'version_compare($.version, "0.10.0")'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.10.0'})
        )
        self.assertEqual(result, 0)

    def test_version_more_than(self):
        expression = 'version_more_than($.version, "0.10.0")'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.9.0'})
        )
        self.assertEqual(result, False)

        expression = 'version_more_than($.version, "0.10.0")'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, True)

        expression = 'version_more_than($.version, "0.10.0")'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.10.0'})
        )
        self.assertEqual(result, False)

    def test_version_less_than(self):
        expression = 'version_less_than($.version, "0.10.0")'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.9.0'})
        )
        self.assertEqual(result, True)

        expression = 'version_less_than($.version, "0.10.0")'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, False)

        expression = 'version_less_than($.version, "0.10.0")'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.10.0'})
        )
        self.assertEqual(result, False)

    def test_version_equal(self):
        expression = 'version_equal($.version, "0.10.0")'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.9.0'})
        )
        self.assertEqual(result, False)

        expression = 'version_equal($.version, "0.10.0")'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, False)

        expression = 'version_equal($.version, "0.10.0")'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.10.0'})
        )
        self.assertEqual(result, True)

    def test_version_match(self):
        expression = 'version_match($.version, ">0.10.0")'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, True)
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.1.1'})
        )
        self.assertEqual(result, False)

        expression = 'version_match($.version, "<0.10.0")'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.1.0'})
        )
        self.assertEqual(result, True)
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '1.1.0'})
        )
        self.assertEqual(result, False)

        expression = 'version_match($.version, "==0.10.0")'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.10.0'})
        )
        self.assertEqual(result, True)
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, False)

    def test_version_bump_major(self):
        expression = 'version_bump_major($.version)'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, '1.0.0')

    def test_version_bump_minor(self):
        expression = 'version_bump_minor($.version)'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, '0.11.0')

    def test_version_bump_patch(self):
        expression = 'version_bump_patch($.version)'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, '0.10.2')

    def test_version_strip_patch(self):
        expression = 'version_strip_patch($.version)'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, '0.10')
