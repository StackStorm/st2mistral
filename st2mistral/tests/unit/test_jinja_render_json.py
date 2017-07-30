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


class JinjaUtilsJsonEscapeTestCase(base.JinjaFunctionTestCase):

    def test_doublequotes(self):
        template = '{{ json_escape(_.test_str) }}'
        result = self.eval_expression(template, {'test_str': 'foo """ bar'})
        self.assertEqual(result, 'foo \\"\\"\\" bar')

    def test_backslashes(self):
        template = '{{ json_escape(_.test_str) }}'
        result = self.eval_expression(template, {'test_str': 'foo \ bar'})
        self.assertEqual(result, 'foo \\\\ bar')

    def test_backspace(self):
        template = '{{ json_escape(_.test_str) }}'
        result = self.eval_expression(template, {'test_str': 'foo \b bar'})
        self.assertEqual(result, 'foo \\b bar')

    def test_formfeed(self):
        template = '{{ json_escape(_.test_str) }}'
        result = self.eval_expression(template, {'test_str': 'foo \f bar'})
        self.assertEqual(result, 'foo \\f bar')

    def test_newline(self):
        template = '{{ json_escape(_.test_str) }}'
        result = self.eval_expression(template, {'test_str': 'foo \n bar'})
        self.assertEqual(result, 'foo \\n bar')

    def test_carriagereturn(self):
        template = '{{ json_escape(_.test_str) }}'
        result = self.eval_expression(template, {'test_str': 'foo \r bar'})
        self.assertEqual(result, 'foo \\r bar')

    def test_tab(self):
        template = '{{ json_escape(_.test_str) }}'
        result = self.eval_expression(template, {'test_str': 'foo \t bar'})
        self.assertEqual(result, 'foo \\t bar')
