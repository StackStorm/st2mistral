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


class JinjaRegexTestCase(base.JinjaFunctionTestCase):

    def test_functions_regex_match(self):
        template = '{{ regex_match(_.k1, "x") }}'
        result = self.eval_expression(template, {'k1': 'xyz'})
        self.assertEqual(result, 'True')

        template = '{{ regex_match(_.k1, "y") }}'
        result = self.eval_expression(template, {'k1': 'xyz'})
        self.assertEqual(result, 'False')

        result = self.eval_expression(
            '{{ regex_match(_.k1, "^v(\\d+\\.)?(\\d+\\.)?(\\*|\\d+)$") }}',
            {'k1': 'v0.10.1'}
        )
        self.assertEqual(result, 'True')

    def test_functions_regex_replace(self):
        template = '{{ regex_replace(_.k1, "x", "y") }}'
        result = self.eval_expression(template, {'k1': 'xyz'})
        self.assertEqual(result, 'yyz')

        result = self.eval_expression(
            '{{ regex_replace(_.k1, "(blue|white|red)", "color") }}',
            {'k1': 'blue socks and red shoes'}
        )
        self.assertEqual(result, 'color socks and color shoes')

    def test_functions_regex_search(self):
        template = '{{ regex_search(_.k1, "x") }}'
        result = self.eval_expression(template, {'k1': 'xyz'})
        self.assertEqual(result, 'True')

        template = '{{ regex_search(_.k1, "y") }}'
        result = self.eval_expression(template, {'k1': 'xyz'})
        self.assertEqual(result, 'True')

        result = self.eval_expression(
            '{{ regex_search(_.k1, "^v(\\d+\\.)?(\\d+\\.)?(\\*|\\d+)$") }}',
            {'k1': 'v0.10.1'}
        )
        self.assertEqual(result, 'True')

    def test_functions_regex_substring(self):
        # Normal (match)
        pattern = "([0-9]{3} \w+ (?:Ave|St|Dr))"
        result = self.eval_expression(
            '{{ regex_substring(_.input_str, "%s") }}' % pattern,
            {'input_str': 'My address is 123 Somewhere Ave. See you soon!'}
        )
        self.assertEqual(result, '123 Somewhere Ave')

        # Selecting second match explicitly
        pattern = "([0-9]{3} \w+ (?:Ave|St|Dr))"
        result = self.eval_expression(
            '{{ regex_substring(_.input_str, "%s", 1) }}' % pattern,
            {'input_str': 'You are at 567 Elsewhere Dr. Im at 123 Foo Ave.'}
        )
        self.assertEqual(result, '123 Foo Ave')

        # Selecting second match explicitly, but doesn't exist
        with self.assertRaises(IndexError):
            pattern = "([0-9]{3} \w+ (?:Ave|St|Dr))"
            result = self.eval_expression(
                '{{ regex_substring(_.input_str, "%s", 1) }}' % pattern,
                {'input_str': 'Your address is 567 Elsewhere Dr.'}
            )

        # No match
        with self.assertRaises(IndexError):
            pattern = "([0-3]{3} \w+ (?:Ave|St|Dr))"
            result = self.eval_expression(
                '{{ regex_substring(_.input_str, "%s") }}' % pattern,
                {'input_str': 'My address is 986 Somewhere Ave. See you soon!'}
            )


class YAQLRegexTestCase(base.YaqlFunctionTestCase):

    def test_functions_regex_match(self):
        context = {
            'k1': 'xyz',
            'pattern': u'x'
        }
        result = YAQL_ENGINE('regex_match($.k1, $.pattern)').evaluate(
            context=self.get_yaql_context(context)
        )
        self.assertTrue(result)

        context = {
            'k1': 'xyz',
            'pattern': u'y'
        }
        result = YAQL_ENGINE('regex_match($.k1, $.pattern)').evaluate(
            context=self.get_yaql_context(context)
        )
        self.assertFalse(result)

        context = {
            'k1': 'v0.10.1',
            'pattern': u'^v(\\d+\\.)?(\\d+\\.)?(\\*|\\d+)$'
        }
        result = YAQL_ENGINE('regex_match($.k1, $.pattern)').evaluate(
            context=self.get_yaql_context(context)
        )
        self.assertTrue(result)

    def test_functions_regex_replace(self):
        context = {
            'k1': u'xyz',
            'pattern': u'x',
            'replacement': u'y'
        }
        expression = 'regex_replace($.k1, $.pattern, $.replacement)'
        actual = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context(context)
        )
        self.assertEqual(actual, 'yyz')

        context = {
            'k1': u'blue socks and red shoes',
            'pattern': u'(blue|white|red)',
            'replacement': u'color'
        }
        expression = 'regex_replace($.k1, $.pattern, $.replacement)'
        actual = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context(context)
        )
        self.assertEqual(actual, 'color socks and color shoes')

    def test_functions_regex_search(self):
        context = {
            'k1': 'xyz',
            'pattern': u'x'
        }
        result = YAQL_ENGINE('regex_search($.k1, $.pattern)').evaluate(
            context=self.get_yaql_context(context)
        )
        self.assertTrue(result)

        context = {
            'k1': 'xyz',
            'pattern': u'y'
        }
        result = YAQL_ENGINE('regex_search($.k1, $.pattern)').evaluate(
            context=self.get_yaql_context(context)
        )
        self.assertTrue(result)

        context = {
            'k1': 'v0.10.1',
            'pattern': u'^v(\\d+\\.)?(\\d+\\.)?(\\*|\\d+)$'
        }
        result = YAQL_ENGINE('regex_search($.k1, $.pattern)').evaluate(
            context=self.get_yaql_context(context)
        )
        self.assertTrue(result)

    def test_functions_regex_substring(self):
        # Normal (match)
        context = {
            'input_str': 'My address is 123 Somewhere Ave. See you soon!',
            'pattern': u'([0-9]{3} \w+ (?:Ave|St|Dr))'
        }
        expression = 'regex_substring($.input_str, $.pattern)'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context(context)
        )
        self.assertEqual(result, '123 Somewhere Ave')

        # Selecting second match explicitly
        context = {
            'input_str': 'You are at 567 Elsewhere Dr. Im at 123 Foo Ave.',
            'pattern': u'([0-9]{3} \w+ (?:Ave|St|Dr))'
        }
        expression = 'regex_substring($.input_str, $.pattern, 1)'
        result = YAQL_ENGINE(expression).evaluate(
            context=self.get_yaql_context(context)
        )
        self.assertEqual(result, '123 Foo Ave')

        # Selecting second match explicitly, but doesn't exist
        context = {
            'input_str': 'Your address is 567 Elsewhere Dr.',
            'pattern': u'([0-9]{3} \w+ (?:Ave|St|Dr))'
        }
        expression = 'regex_substring($.input_str, $.pattern, 1)'
        with self.assertRaises(IndexError):
            result = YAQL_ENGINE(expression).evaluate(
                context=self.get_yaql_context(context)
            )

        # No match
        context = {
            'input_str': 'My address is 986 Somewhere Ave. See you soon!',
            'pattern': u'([0-3]{3} \w+ (?:Ave|St|Dr))'
        }

        with self.assertRaises(IndexError):
            expression = 'regex_substring($.input_str, $.pattern, 1)'
            result = YAQL_ENGINE(expression).evaluate(
                context=self.get_yaql_context(context)
            )
