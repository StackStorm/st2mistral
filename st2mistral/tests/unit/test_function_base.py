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

from functools import partial
import unittest2
import yaql

ROOT_YAQL_CONTEXT = None


def get_functions():
    from st2mistral.functions import data
    from st2mistral.functions import json_escape
    from st2mistral.functions import jsonpath_query
    from st2mistral.functions import regex
    from st2mistral.functions import time
    from st2mistral.functions import use_none
    from st2mistral.functions import version

    return {
        'from_json_string': data.from_json_string,
        'from_yaml_string': data.from_yaml_string,
        'json_escape': json_escape.json_escape,
        'jsonpath_query': jsonpath_query.jsonpath_query,
        'regex_match': regex.regex_match,
        'regex_replace': regex.regex_replace,
        'regex_search': regex.regex_search,
        'regex_substring': regex.regex_substring,
        'to_complex': data.to_complex,
        'to_human_time_from_seconds': time.to_human_time_from_seconds,
        'to_json_string': data.to_json_string,
        'to_yaml_string': data.to_yaml_string,
        'use_none': use_none.use_none,
        'version_compare': version.version_compare,
        'version_bump_major': version.version_bump_major,
        'version_bump_minor': version.version_bump_minor,
        'version_bump_patch': version.version_bump_patch,
        'version_equal': version.version_equal,
        'version_less_than': version.version_less_than,
        'version_match': version.version_match,
        'version_more_than': version.version_more_than,
        'version_strip_patch': version.version_strip_patch
    }


class JinjaFunctionTestCase(unittest2.TestCase):
    """Infrastructure to allow Jinja tests to render expressions like Mistral does

    """

    def setUp(self):
        env = self.get_jinja_environment()
        self._env = env.overlay()

    def get_jinja_environment(self, allow_undefined=False, trim_blocks=True,
                              lstrip_blocks=True):
        """jinja2.Environment object setup with right behaviors and functions

        :param strict_undefined: allow undefined variables in templates
        :type strict_undefined: ``bool``

        """
        # Late import to avoid very expensive in-direct import (~1 second)
        # when this function is not called / used
        import jinja2

        undefined = (jinja2.Undefined if allow_undefined
                     else jinja2.StrictUndefined)
        env = jinja2.Environment(  # nosec
            undefined=undefined,
            trim_blocks=trim_blocks,
            lstrip_blocks=lstrip_blocks
        )
        env.filters.update(get_functions())
        env.tests['in'] = lambda item, list: item in list
        return env

    def eval_expression(self, expression, context):
        ctx = self.get_jinja_context(context)
        return self._env.from_string(expression).render(**ctx)

    def get_jinja_context(self, data_context):
        new_ctx = {
            '_': data_context
        }

        self._register_jinja_functions(new_ctx)

        if isinstance(data_context, dict):
            new_ctx['__env'] = data_context.get('__env')
            new_ctx['__execution'] = data_context.get('__execution')
            new_ctx['__task_execution'] = data_context.get('__task_execution')

        return new_ctx

    def _register_jinja_functions(self, jinja_ctx):
        functions = get_functions()

        for name in functions:
            jinja_ctx[name] = partial(functions[name], jinja_ctx['_'])


class YaqlFunctionTestCase(unittest2.TestCase):

    def get_yaql_context(self, data_context):
        global ROOT_YAQL_CONTEXT

        if not ROOT_YAQL_CONTEXT:
            ROOT_YAQL_CONTEXT = yaql.create_context()

            self._register_yaql_functions(ROOT_YAQL_CONTEXT)

        new_ctx = ROOT_YAQL_CONTEXT.create_child_context()
        new_ctx['$'] = data_context

        if isinstance(data_context, dict):
            new_ctx['__env'] = data_context.get('__env')
            new_ctx['__execution'] = data_context.get('__execution')
            new_ctx['__task_execution'] = data_context.get('__task_execution')

        return new_ctx

    def _register_yaql_functions(self, yaql_ctx):
        functions = get_functions()

        for name in functions:
            yaql_ctx.register_function(functions[name], name=name)
