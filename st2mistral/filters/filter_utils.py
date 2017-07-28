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

def _intercept_context(func):
    """Decorator for smoothing out variations in the way filters are called

    Used as a decorator, this function will detect if the first positional argument
    is a dict, (which means the Mistral context is being passed first), and removes it.

    TODO(mierdin): An alternative approach to simply removing the context from args would be to
    transform it to a keyword arg, and add context as an optional kwarg for each filter
    function. However, none of the functions would currently use it, so that's its own
    style issue. Should consider this further.
    """

    def func_wrapper(*args, **kwargs):
        first_arg = args[0]
        if isinstance(first_arg, dict):
            args = args[1:]
        return func(*args, **kwargs)
    return func_wrapper
