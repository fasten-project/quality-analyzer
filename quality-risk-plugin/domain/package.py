"""
This module contains all the classes related to a product, such as
Module, File, Method.
"""
# TODO: language specific, mvp starts from Maven and Java

import logging
from _datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional

import lizard
import lizard_languages

logger = logging.getLogger(__name__)


class Package:
    """
    This class defines the metadata of a package,
    extracted from FASTEN call graph Json file.
    """

    def __int__(self, cg):
        self.forge = cg.forge
        self.product = cg.product
        self.version = cg.version
        self._func_list = []  # type: List[Function] # extracted from lizard
        self._method_list = []  # extracted from call graph or not needed, this can be get from cg
        # aggregated metric of lizard results
        self.method_count = None
        self.noc = None
        self.complexity = None

        """
        type: List[Method]  or List[str] or Map[] extracted from cg todo: type need to decide
        Todo: data structures for lists of internal nodes (methods) and external nodes (methods) in call graph,
                 and a mapping between method name in cg and in lizard.
        """

class Dependency:
    """
    This class defines the (direct?) dependencies of a package,
    extracted from FASTEN call graph Json file.
    """

    def __int__(self, cg):
        self._dep_list = []  # type: List[Package]


class Function:
    """
    This class represents a function in a class. Contains various information,
    extracted through Lizard.
    """

    def __init__(self, func):
        """
        Initialize a function object. This is calculated using Lizard: it parses
        the source code of all the modifications in a commit, extracting
        information of the methods contained in the file (if the file is a
        source code written in one of the supported programming languages).
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

    UNIT_SIZE_LOW_RISK_THRESHOLD = 15
    """
    Threshold used in the Delta Maintainability Model to establish whether a method
    is low risk in terms of its size.
    The procedure to obtain the threshold is described in the
    :ref:`PyDriller documentation <Properties>`.
    """

    UNIT_COMPLEXITY_LOW_RISK_THRESHOLD = 5
    """
    Threshold used in the Delta Maintainability Model to establish whether a method
    is low risk in terms of its cyclomatic complexity.
    The procedure to obtain the threshold is described in the
    :ref:`PyDriller documentation <Properties>`.
    """

    UNIT_INTERFACING_LOW_RISK_THRESHOLD = 2
    """
    Threshold used in the Delta Maintainability Model to establish whether a method
    is low risk in terms of its interface.
    The procedure to obtain the threshold is described in the
    :ref:`PyDriller documentation <Properties>`.
    """



