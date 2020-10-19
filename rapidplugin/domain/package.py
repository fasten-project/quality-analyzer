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

"""
This module contains all the classes related to a product, such as
Module, File, Method.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional

logger = logging.getLogger(__name__)


class Package(ABC):
    """
    This class defines the metadata of a package.
    """

    def __init__(self, forge, product, version, path):
        self.forge = forge
        self.product = product
        self.version = version
        self.source_path = path
        self._file_list = []
        self._func_list = []
        # aggregated metric
        self._method_count = None
        self._nloc = None
        self._complexity = None
        self._token_count = None
        self._ND = None

    def nloc(self) -> Optional[int]:
        self._calculate_metrics()
        return self._nloc

    def method_count(self) -> Optional[int]:
        self._calculate_metrics()
        return self._method_count

    def complexity(self) -> Optional:
        self._calculate_metrics()
        return self._complexity

    def token_count(self) -> Optional:
        self._calculate_metrics()
        return self._token_count

    @abstractmethod
    def _calculate_metrics(self):
        """calculate metrics.

        Args:

        """
    @abstractmethod
    def _get_analyzer(self):
        """get analyzer name and version.

        """

    def files(self):
        return self._file_list

    def functions(self):
        return self._func_list

    def metadata(self):
        language = {
            'mvn': 'java',
            'debian': 'c',
            'PyPI': 'python'
        }
        m = {
            "product": self.product,
            "version": self.version,
            "forge": self.forge,
            "language": language[self.forge]
        }
        m.update(self._get_analyzer())
        return m

    def metrics(self):
        return {
            "metrics": {
                "nloc": self.nloc(),
                "method_count": self.method_count(),
                "complexity": self.complexity(),
                "token_count": self.token_count()
            }
        }


class File(ABC):
    def __init__(self):
        """
        Initialize a function object.
        """
        self.filename = None
        self.nloc = None
        self.token_count = None
        self.function_list = []
        self.average_nloc = None
        self.average_token_count = None
        self.average_cyclomatic_complexity = None
        self.CCN = None
        self.ND = None

    def metrics(self):
        return {
            "filename": self.filename,
            "nloc": self.nloc,
            "average_nloc": self.average_nloc,
            "average_token_count": self.average_token_count,
            "average_cyclomatic_complexity": self.average_cyclomatic_complexity,
            "CCN": self.CCN,
            "ND": self.ND
        }


class Dependency:

    def __int__(self):
        pass


class Function(ABC):
    """
    This class represents a function in a package. Contains various information,
    extracted through Lizard.
    """

    def __init__(self):
        """
        Initialize a function object.
        """
        self.name = None
        self.long_name = None
        self.filename = None
        self.nloc = None
        self.complexity = None
        self.token_count = None
        self.parameters = None
        self.start_line = None
        self.end_line = None
        self.fan_in = None
        self.fan_out = None
        self.general_fan_out = None
        self.length = None
        self.top_nesting_level = None

    def metadata(self):
        return {
            "filename": self.filename,
            "name": self.name,
            "long_name": self.long_name,
            "start_line": self.start_line,
            "end_line": self.end_line
        }

    def metrics(self):
        return {
            "metrics": {
                "nloc": self.nloc,
                "complexity": self.complexity,
                "token_count": self.token_count,
                "parameters": self.parameters,
                "length": self.length
            }
        }

    def __eq__(self, other):
        return self.name == other.name and self.parameters == other.parameters

    def __hash__(self):
        return hash(('name', self.name,
                     'long_name', self.long_name,
                     'params', (x for x in self.parameters)))





