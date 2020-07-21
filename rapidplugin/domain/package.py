"""
This module contains all the classes related to a product, such as
Module, File, Method.
"""

import logging
from _datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional


logger = logging.getLogger(__name__)


class Package:
    """
    This class defines the metadata of a package,
    extracted from FASTEN call graph Json file.
    """

    def __int__(self, forge, product, version):
        self.forge = forge
        self.product = product
        self.version = version
        self.path = None
        self._file_list = []
        self._func_list = []  # type: List[Function] # extracted from lizard
        self._method_list = []  # extracted from call graph or not needed, this can be get from cg
        # aggregated metric of lizard results
        self._method_count = None
        self._nloc = None
        self._complexity = None

        """
        type: List[Method] or List[str] or Map[] extracted from cg. type need to decide,
        data structures for lists of internal nodes (methods) and external nodes (methods) in call graph,
                 and a mapping between method name in cg and in lizard.
        """
    def nloc(self) -> Optional[int]:
        self._calculate_metrics()
        return self._nloc

    def method_count(self) -> Optional[int]:
        self._calculate_metric()
        return self._method_count

    def complexity(self) -> Optional:
        self._calculate_metric()
        return self._complexity

    def _calculate_metric(self):
        return


class Dependency:
    """
    This class defines the (direct?) dependencies of a package,
    extracted from FASTEN call graph Json file.
    """

    def __int__(self, cg):
        self._dep_list = []  # type: List[Package]


class Function:
    """
    This class represents a function in a package. Contains various information,
    extracted through Lizard.
    """

    def __init__(self, func):
        """
        Initialize a function object. This is calculated using Lizard
        """
        self.name = func.name
        self.long_name = func.long_name
        self.filename = func.filename
        self.nloc = func.nloc
        self.complexity = func.cyclomatic_complexity
        self.token_count = func.token_count
        self.parameters = func.parameters
        self.start_line = func.start_line
        self.end_line = func.end_line
        self.fan_in = func.fan_in
        self.fan_out = func.fan_out
        self.general_fan_out = func.general_fan_out
        self.length = func.length
        self.top_nesting_level = func.top_nesting_level

    def __eq__(self, other):
        return self.name == other.name and self.parameters == other.parameters

    def __hash__(self):
        # parameters are used in hashing in order to
        # prevent collisions when overloading method names
        return hash(('name', self.name,
                     'long_name', self.long_name,
                     'params', (x for x in self.parameters)))





