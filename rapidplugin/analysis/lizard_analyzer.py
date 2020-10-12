# Copyright 2020 Software Improvement Group
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
import lizard

from rapidplugin.domain.package import Package, File, Function


class LizardPackage(Package):

    def __init__(self, forge, product, version, path):
        super.__init__(forge, product, version, path)

    def _calculate_metrics(self):
        paths = [self.source_pathpath]
        exc_patterns = None
        ext = None
        lans = ["java", "python", "cpp"]
        if self._nloc is None:
            self._nloc = 0
            self._method_count = 0
            self._complexity = 0
            self._token_count = 0
            self._ND = 0
            analyser = lizard.analyze(paths, exc_patterns, 1, ext, lans)
            for file in analyser:
                self._file_list.append(LizardFile(file))
                for fun in file.function_list:
                    self._func_list.append(LizardFunction(fun))
                self._nloc += file.nloc
                self._method_count += len(file.function_list)
                self._complexity += file.CCN
                self._ND += file.ND
                self._token_count += file.token_count
        return

    def _get_analyzer(self):
        return {
            "analyzer_name": "lizard",
            "analyzer_version": lizard.version
        }


class LizardFile(File):
    def __init__(self, file_info):
        self.filename = file_info.filename
        self.nloc = file_info.nloc
        self.token_count = file_info.token_count
        self.function_list = [Function(x) for x in file_info.function_list]
        self.average_nloc = file_info.average_nloc
        self.average_token_count = file_info.average_token_count
        self.average_cyclomatic_complexity = file_info.average_cyclomatic_complexity
        self.CCN = file_info.CCN
        self.ND = file_info.ND


class LizardFunction(Function):
    def __init__(self, func):
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
