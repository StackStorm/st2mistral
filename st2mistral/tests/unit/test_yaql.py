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


class TestCaseYaqlComplex(base.YaqlFunctionTestCase):

    def test_to_complex(self):

        obj = {'a': 'b', 'c': {'d': 'e', 'f': 1, 'g': True}}
        result = YAQL_ENGINE('to_complex($.k1)').evaluate(
            context=self.get_yaql_context({'k1': obj})
        )
        actual_obj = json.loads(result)
        self.assertDictEqual(obj, actual_obj)


class TestCaseYaqlData(base.YaqlFunctionTestCase):

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


class TestCaseYaqlJsonEscape(base.YaqlFunctionTestCase):

    def test_doublequotes(self):

        actual = YAQL_ENGINE('json_escape($.k1)').evaluate(
            context=self.get_yaql_context({'k1': 'foo """ bar'})
        )
        expected = 'foo \\"\\"\\" bar'
        self.assertEqual(actual, expected)

    def test_backslashes(self):

        actual = YAQL_ENGINE('json_escape($.k1)').evaluate(
            context=self.get_yaql_context({'k1': 'foo \ bar'})
        )
        expected = 'foo \\\\ bar'
        self.assertEqual(actual, expected)

    def test_backspace(self):

        actual = YAQL_ENGINE('json_escape($.k1)').evaluate(
            context=self.get_yaql_context({'k1': 'foo \b bar'})
        )
        expected = 'foo \\b bar'
        self.assertEqual(actual, expected)

    def test_formfeed(self):

        actual = YAQL_ENGINE('json_escape($.k1)').evaluate(
            context=self.get_yaql_context({'k1': 'foo \f bar'})
        )
        expected = 'foo \\f bar'
        self.assertEqual(actual, expected)

    def test_newline(self):

        actual = YAQL_ENGINE('json_escape($.k1)').evaluate(
            context=self.get_yaql_context({'k1': 'foo \n bar'})
        )
        expected = 'foo \\n bar'
        self.assertEqual(actual, expected)

    def test_carriagereturn(self):

        actual = YAQL_ENGINE('json_escape($.k1)').evaluate(
            context=self.get_yaql_context({'k1': 'foo \r bar'})
        )
        expected = 'foo \\r bar'
        self.assertEqual(actual, expected)

    def test_tab(self):

        actual = YAQL_ENGINE('json_escape($.k1)').evaluate(
            context=self.get_yaql_context({'k1': 'foo \t bar'})
        )
        expected = 'foo \\t bar'
        self.assertEqual(actual, expected)


class TestCaseYaqlRegex(base.YaqlFunctionTestCase):

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


class TestCaseYaqlTime(base.YaqlFunctionTestCase):

    def test_to_human_time_from_seconds(self):

        result = YAQL_ENGINE('to_human_time_from_seconds($.input_int)').evaluate(
            context=self.get_yaql_context({"input_int": 12345})
        )
        self.assertEqual(result, '3h25m45s')

        result = YAQL_ENGINE('to_human_time_from_seconds($.input_int)').evaluate(
            context=self.get_yaql_context({"input_int": 0})
        )
        self.assertEqual(result, '0s')

        with self.assertRaises(AssertionError):
            YAQL_ENGINE('to_human_time_from_seconds($.input_int)').evaluate(
                context=self.get_yaql_context({"input_int": "foo"})
            )


class TestCaseYaqlUseNone(base.YaqlFunctionTestCase):

    def test_use_none(self):

        result = YAQL_ENGINE('use_none($.input_str)').evaluate(
            context=self.get_yaql_context({"input_str": None})
        )
        self.assertEqual(result, '%*****__%NONE%__*****%')

        result = YAQL_ENGINE('use_none($.input_str)').evaluate(
            context=self.get_yaql_context({"input_str": "foobar"})
        )
        self.assertEqual(result, 'foobar')


class TestCaseYaqlVersionFunctions(base.YaqlFunctionTestCase):

    def test_version_compare(self):

        result = YAQL_ENGINE('version_compare($.version, "0.10.0")').evaluate(
            context=self.get_yaql_context({'version': '0.9.0'})
        )
        self.assertEqual(result, -1)

        result = YAQL_ENGINE('version_compare($.version, "0.10.0")').evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, 1)

        result = YAQL_ENGINE('version_compare($.version, "0.10.0")').evaluate(
            context=self.get_yaql_context({'version': '0.10.0'})
        )
        self.assertEqual(result, 0)

    def test_version_more_than(self):

        result = YAQL_ENGINE('version_more_than($.version, "0.10.0")').evaluate(
            context=self.get_yaql_context({'version': '0.9.0'})
        )
        self.assertEqual(result, False)

        result = YAQL_ENGINE('version_more_than($.version, "0.10.0")').evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, True)

        result = YAQL_ENGINE('version_more_than($.version, "0.10.0")').evaluate(
            context=self.get_yaql_context({'version': '0.10.0'})
        )
        self.assertEqual(result, False)

    def test_version_less_than(self):

        result = YAQL_ENGINE('version_less_than($.version, "0.10.0")').evaluate(
            context=self.get_yaql_context({'version': '0.9.0'})
        )
        self.assertEqual(result, True)

        result = YAQL_ENGINE('version_less_than($.version, "0.10.0")').evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, False)

        result = YAQL_ENGINE('version_less_than($.version, "0.10.0")').evaluate(
            context=self.get_yaql_context({'version': '0.10.0'})
        )
        self.assertEqual(result, False)

    def test_version_equal(self):

        result = YAQL_ENGINE('version_equal($.version, "0.10.0")').evaluate(
            context=self.get_yaql_context({'version': '0.9.0'})
        )
        self.assertEqual(result, False)

        result = YAQL_ENGINE('version_equal($.version, "0.10.0")').evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, False)

        result = YAQL_ENGINE('version_equal($.version, "0.10.0")').evaluate(
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

        result = YAQL_ENGINE('version_bump_major($.version)').evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, '1.0.0')

    def test_version_bump_minor(self):

        result = YAQL_ENGINE('version_bump_minor($.version)').evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, '0.11.0')

    def test_version_bump_patch(self):

        result = YAQL_ENGINE('version_bump_patch($.version)').evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, '0.10.2')

    def test_version_strip_patch(self):

        result = YAQL_ENGINE('version_strip_patch($.version)').evaluate(
            context=self.get_yaql_context({'version': '0.10.1'})
        )
        self.assertEqual(result, '0.10')
