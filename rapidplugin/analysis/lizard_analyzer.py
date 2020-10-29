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

import os
import logging
import datetime
from pathlib import Path

import lizard

from rapidplugin.domain.package import Package, File, Function
from rapidplugin.utils.utils import MavenUtils

logger = logging.getLogger(__name__)


class LizardAnalyzer:
    def __init__(self, base_dir):
        self.analyzer_name = "Lizard"
        self.base_dir = base_dir

    def analyze(self, payload):
        '''
        TODO
        '''
        out_payloads = []
        forge = payload['forge']
        product = payload['groupId'] + ":" + payload['artifactId'] if forge == "mvn" else payload['product']
        version = payload['version']
        with self.get_source_path(payload) as path:
            package = LizardPackage(forge, product, version, str(path))
        metadata = package.metadata()
        for function in package.functions():
            m = {}
            m.update(metadata)
            m.update(function.metadata())
            m.update(function.metrics())
            out_payloads.append(m)
            logger.debug("callable: {}".format(m) + '\n')
        return out_payloads

    def get_source_path(self, payload):
        """
        TODO: consider moving this to a utility class.
        For maven, the order to get source code path from different sources:
        [x] 1. if *-sources.jar is valid, download,
               uncompress and return the path to the source code
        [x] 2. else if repoPath is not empty, and
        [x]    2.1 if commit tag is valid, checkout based on tag and return the path
        [ ]    2.2 if needed, checkout based on the release date.
        [x] 3. else return None and raise exception (Cannot get source code)
        """
        base_dir = Path(self.base_dir)
        if not base_dir.exists():
            base_dir.mkdir(parents=True)
        source_path = None
        if payload['forge'] == "mvn":
            if 'sourcesUrl' in payload:
                sources_url = payload['sourcesUrl']
                if sources_url != "":
                    source_path = MavenUtils.download_jar(sources_url, base_dir)
            elif 'repoPath' in payload and 'commitTag' in payload and 'repoType' in payload:
                repo_path = payload['repoPath']
                repo_type = payload['repoType']
                commit_tag = payload['commitTag']
                source_path = MavenUtils.checkout_version(repo_path, repo_type, commit_tag, base_dir)
            assert source_path is not None, \
                f"Cannot get source code for '{payload['groupId']}:{payload['artifactId']}:{payload['version']}'."
            return source_path
        else:
            assert 'sourcePath' in payload, \
                f"Cannot get source code for '{payload['product']}:{payload['version']}', missing 'sourcePath'."
            source_path = payload['sourcePath']
            assert source_path != "", \
                f"Cannot get source code for '{payload['product']}:{payload['version']}', empty 'sourcePath."
            assert os.path.isabs(source_path), "sourcePath: '{}' is not an absolute path!".format(source_path)
            source_path = MavenUtils.copy_source(payload['sourcePath'], base_dir)
            return source_path


class LizardPackage(Package):

    def __init__(self, forge, product, version, path):
        super().__init__(forge, product, version, path)
        self.timestamp = None
        self._calculate_metrics()

    def _calculate_metrics(self):
        paths = [self.source_path]
        exc_patterns = None
        ext = None
        lans = ["java", "python", "cpp"]
        self.timestamp = str(datetime.datetime.now().timestamp())
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
                # self._ND += file.ND
                self._token_count += file.token_count
        return

    def _get_analyzer(self):
        return {
            "analyzer_name": "lizard",
            "analyzer_version": lizard.version,
            "analysis_timestamp": self.timestamp
        }


class LizardFile(File):
    def __init__(self, file_info):
        super().__init__()
        self.filename = file_info.filename
        self.nloc = file_info.nloc
        self.token_count = file_info.token_count
        self.function_list = [LizardFunction(x) for x in file_info.function_list]
        self.average_nloc = file_info.average_nloc
        self.average_token_count = file_info.average_token_count
        self.average_cyclomatic_complexity = file_info.average_cyclomatic_complexity
        self.CCN = file_info.CCN


class LizardFunction(Function):
    def __init__(self, func_info):
        super().__init__()
        self.name = func_info.name
        self.long_name = func_info.long_name
        self.filename = func_info.filename
        self.nloc = func_info.nloc
        self.complexity = func_info.cyclomatic_complexity
        self.token_count = func_info.token_count
        self.parameters = func_info.parameters
        self.start_line = func_info.start_line
        self.end_line = func_info.end_line
        self.fan_in = func_info.fan_in
        self.fan_out = func_info.fan_out
        self.general_fan_out = func_info.general_fan_out
        self.length = func_info.length
        self.top_nesting_level = func_info.top_nesting_level
