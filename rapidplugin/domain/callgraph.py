# Copyright 2020 Software Improvement Group
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from enum import Enum

"""
This module contains all the classes related to a call graph, such as
Method, Call, extracted from FASTEN call graph json file.
"""


class CallGraph:

    def __init__(self, path: str):
        self._path = path
        self.forge = None
        self.product = None
        self.version = None
        self._method_list = []
        self._call_list = []


class MethodType(Enum):

    INTERNAL = 1
    EXTERNAL = 2


class MethodAccess(Enum):

    PUBLIC = 1
    PRIVATE = 2


class CallType(Enum):

    INTERNAL = 1
    EXTERNAL = 2


class Method:

    def __int__(self):
        self.name = None
        self.method_type = None
        self.method_access = None


class Call:

    def __int__(self):
        self._source = None
        self._target = None
        self.call_type = None

