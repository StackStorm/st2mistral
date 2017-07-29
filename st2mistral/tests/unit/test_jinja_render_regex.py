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


class JinjaUtilsRegexFunctionTestCase(base.JinjaFunctionTestCase):

    def test_functions_regex_match(self):

        template = '{{ regex_match(_.k1, "x") }}'
        result = self.eval_expression(template, {'k1': 'xyz'})
        self.assertEqual(result, 'True')

        template = '{{ regex_match(_.k1, "y") }}'
        result = self.eval_expression(template, {'k1': 'xyz'})
        self.assertEqual(result, 'False')

        template = '{{ regex_match(_.k1, "^v(\\d+\\.)?(\\d+\\.)?(\\*|\\d+)$") }}'
        result = self.eval_expression(template, {'k1': 'v0.10.1'})
        self.assertEqual(result, 'True')

    def test_functions_regex_replace(self):

        template = '{{ regex_replace(_.k1, "x", "y") }}'
        result = self.eval_expression(template, {'k1': 'xyz'})
        self.assertEqual(result, 'yyz')

        template = '{{ regex_replace(_.k1, "(blue|white|red)", "color") }}'
        result = self.eval_expression(template, {'k1': 'blue socks and red shoes'})
        self.assertEqual(result, 'color socks and color shoes')

    def test_functions_regex_search(self):

        template = '{{ regex_search(_.k1, "x") }}'
        result = self.eval_expression(template, {'k1': 'xyz'})
        self.assertEqual(result, 'True')

        template = '{{ regex_search(_.k1, "y") }}'
        result = self.eval_expression(template, {'k1': 'xyz'})
        self.assertEqual(result, 'True')

        template = '{{ regex_search(_.k1, "^v(\\d+\\.)?(\\d+\\.)?(\\*|\\d+)$") }}'
        result = self.eval_expression(template, {'k1': 'v0.10.1'})
        self.assertEqual(result, 'True')

    def test_functions_regex_substring(self):

        # Normal (match)
        template = '{{ regex_substring(_.input_str, "([0-9]{3} \w+ (?:Ave|St|Dr))") }}'
        result = self.eval_expression(
            template,
            {'input_str': 'My address is 123 Somewhere Ave. See you soon!'}
        )
        self.assertEqual(result, '123 Somewhere Ave')

        # Selecting second match explicitly
        template = '{{ regex_substring(_.input_str, "([0-9]{3} \w+ (?:Ave|St|Dr))", 1) }}'
        result = self.eval_expression(
            template,
            {'input_str': 'Your address is 567 Elsewhere Dr. My address is 123 Somewhere Ave.'}
        )
        self.assertEqual(result, '123 Somewhere Ave')

        # Selecting second match explicitly, but doesn't exist
        template = '{{ regex_substring(_.input_str, "([0-9]{3} \w+ (?:Ave|St|Dr))", 1) }}'
        with self.assertRaises(IndexError):
            result = self.eval_expression(
                template,
                {'input_str': 'Your address is 567 Elsewhere Dr.'}
            )

        # No match
        template = '{{ regex_substring(_.input_str, "([0-3]{3} \w+ (?:Ave|St|Dr))") }}'
        with self.assertRaises(IndexError):
            result = self.eval_expression(
                template,
                {'input_str': 'My address is 986 Somewhere Ave. See you soon!'}
            )
