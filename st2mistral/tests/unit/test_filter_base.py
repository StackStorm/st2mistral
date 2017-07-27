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

import unittest2
import yaql


def get_filters():
    from st2mistral.filters import complex_type
    from st2mistral.filters import data
    from st2mistral.filters import json_escape
    from st2mistral.filters import regex
    from st2mistral.filters import time
    from st2mistral.filters import use_none
    from st2mistral.filters import version

    return {
        'to_json_string': data.to_json_string,
        'to_yaml_string': data.to_yaml_string,

        'to_complex': complex_type.to_complex,

        'json_escape': json_escape.json_escape,

        'regex_match': regex.regex_match,
        'regex_replace': regex.regex_replace,
        'regex_search': regex.regex_search,
        'regex_substring': regex.regex_substring,

        'to_human_time_from_seconds': time.to_human_time_from_seconds,

        'use_none': use_none.use_none,

        'version_compare': version.version_compare,
        'version_more_than': version.version_more_than,
        'version_less_than': version.version_less_than,
        'version_equal': version.version_equal,
        'version_match': version.version_match,
        'version_bump_major': version.version_bump_major,
        'version_bump_minor': version.version_bump_minor,
        'version_bump_patch': version.version_bump_patch,
        'version_strip_patch': version.version_strip_patch
    }


class JinjaFilterTestCase(unittest2.TestCase):

    def get_jinja_environment(self, allow_undefined=False, trim_blocks=True, lstrip_blocks=True):
        """jinja2.Environment object that is setup with right behaviors and custom filters.

        :param strict_undefined: If should allow undefined variables in templates
        :type strict_undefined: ``bool``

        """
        # Late import to avoid very expensive in-direct import (~1 second) when this function
        # is not called / used
        import jinja2

        undefined = jinja2.Undefined if allow_undefined else jinja2.StrictUndefined
        env = jinja2.Environment(  # nosec
            undefined=undefined,
            trim_blocks=trim_blocks,
            lstrip_blocks=lstrip_blocks
        )
        env.filters.update(get_filters())
        env.tests['in'] = lambda item, list: item in list
        return env
