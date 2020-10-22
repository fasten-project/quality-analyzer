
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

import os
import pytest
from rapidplugin.tests.sources import sources
from rapidplugin.tests.sources import fix_sourcePath
from rapidplugin.analysis.lizard_analyzer import LizardAnalyzer


@pytest.fixture(scope='session')
def analyzer(sources):
    yield LizardAnalyzer(str(sources))

mvn_libai_1_6_12 = {
    "forge": "mvn",
    "groupId": "ai.api",
    "artifactId": "libai",
    "version": "1.6.12",
    "sourcesUrl": "https://repo1.maven.org/maven2/ai/api/libai/1.6.12/libai-1.6.12-sources.jar",
    "repoPath": "",
    "repoType": "",
    "commitTag": ""
}
mvn_message_with_source_url = {
    "forge": "mvn",
    "groupId": "test-mvn",
    "artifactId": "m1",
    "version": "1.0.0",
    "sourcesUrl": "maven/m1/m1.jar",
    "repoPath": "",
    "repoType": "",
    "commitTag": ""
}
mvn_message_with_git_repo = {
    "forge": "mvn",
    "groupId": "test-mvn",
    "artifactId": "m1",
    "version": "1.0.0",
    "sourcesUrl": "",
    "repoPath": "maven/git/m1",
    "repoType": "git",
    "commitTag": "1.0.0"
}
mvn_message_with_svn_repo = {
    "forge": "mvn",
    "groupId": "test-mvn",
    "artifactId": "m2",
    "version": "1.0.0",
    "sourcesUrl": "",
    "repoPath": "maven/svn/m2",
    "repoType": "svn",
    "commitTag": "1.0.0"
}
mvn_message_with_hg_repo = {
    "forge": "mvn",
    "groupId": "test-mvn",
    "artifactId": "m3",
    "version": "1.0.0",
    "sourcesUrl": "",
    "repoPath": "maven/hg/m3",
    "repoType": "hg",
    "commitTag": "1.0.0"
}
debian_message = {
    "forge": "debian",
    "product": "d1",
    "version": "1.0.0",
    "sourcePath": "debian/d1"
}
pypi_message = {
    "forge": "PyPI",
    "product": "p1",
    "version": "1.0.0",
    "sourcePath": "pypi/p1"
}

# List of (payload, function_count) pairs
FUNCTION_COUNT_DATA = [
    (mvn_libai_1_6_12, 411),
    (debian_message, 1),
    (pypi_message, 1)
]

# List of (payload, start_line, end_line) tuples
FUNCTION_LINE_DATA = [
    # (mvn_message_with_repo, 2, 4),
    (debian_message, 3, 3),
    (pypi_message, 1, 2)
]

# List of (payload, nloc, complexity, token_count) tuples
FUNCTION_METRICS_DATA = [
    # (mvn_message_with_repo, 3, 1, 18),
    (debian_message, 1, 1, 5),
    (pypi_message, 2, 1, 5)
]


@pytest.mark.parametrize('record,fc', FUNCTION_COUNT_DATA)
def test_function_count(analyzer, sources, record, fc: int):
    out_payloads = analyzer.analyze(fix_sourcePath(record, sources))
    assert len(out_payloads) == fc


@pytest.mark.parametrize('record,start_line,end_line', FUNCTION_LINE_DATA)
def test_function_location(analyzer, sources, record, start_line: int, end_line: int):
    out_payloads = analyzer.analyze(fix_sourcePath(record, sources))
    metadata = out_payloads[0]
    assert metadata['start_line'] == start_line
    assert metadata['end_line'] == end_line


@pytest.mark.parametrize('record,nloc,complexity,token_count', FUNCTION_METRICS_DATA)
def test_function_metrics(analyzer, sources, record, nloc: int, complexity: int, token_count: int):
    out_payloads = analyzer.analyze(fix_sourcePath(record, sources))
    metrics = out_payloads[0]['metrics']
    assert metrics['nloc'] == nloc
    assert metrics['complexity'] == complexity
    assert metrics['token_count'] == token_count
