from enum import Enum

"""
This module contains all the classes related to a call graph, such as
Method, Call, extracted from FASTEN call graph json file.
"""


class CallGraph:

    def __int__(self, path: str):
        self._path = path
        self.forge = None
        self.product = None
        self.version = None
        self._method_list = []
        self._call_list = []
        # todo: use map?


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

