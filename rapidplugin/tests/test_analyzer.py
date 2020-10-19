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

import pytest
from analysis.lizard_analyzer import LizardAnalyzer


@pytest.fixture
def analyzer():
    analyzer = LizardAnalyzer("/tmp")
    yield analyzer
    analyzer.clean_up()


mvn_message_with_source_url = {
    "forge": "mvn",
    "groupId": "test-mvn",
    "artifactId": "m1",
    "version": "1.0.0",
    "sourceURL": "/maven/m1/m1.jar",
    "repoPath": "",
    "repoType": "",
    "commitTag": ""
}
mvn_message_with_repo = {
    "forge": "mvn",
    "groupId": "test-mvn",
    "artifactId": "m1",
    "version": "1.0.0",
    "sourceURL": "",
    "repoPath": "tmp/maven/m1",
    "repoType": "git",
    "commitTag": "1.0.0"
}
debian_message = {
    "forge": "debian",
    "product": "d1",
    "version": "1.0.0",
    "sourcePath": "tmp/debian/d1"
}
pypi_message = {
    "forge": "PyPI",
    "product": "p1",
    "version": "1.0.0",
    "sourcePath": "tmp/pypi/p1"
}

# List of (payload, function_count) pairs
FUNCTION_COUNT_DATA = [
    # (mvn_message_with_repo, 1),
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
def test_function_count(analyzer: LizardAnalyzer, record, fc: int):
    out_payloads = analyzer.analyze(record)
    assert len(out_payloads) == fc


@pytest.mark.parametrize('record,start_line,end_line', FUNCTION_LINE_DATA)
def test_function_location(analyzer: LizardAnalyzer, record, start_line: int, end_line: int):
    out_payloads = analyzer.analyze(record)
    metadata = out_payloads[0]
    assert metadata['start_line'] == start_line
    assert metadata['end_line'] == end_line


@pytest.mark.parametrize('record,nloc,complexity,token_count', FUNCTION_METRICS_DATA)
def test_function_metrics(analyzer: LizardAnalyzer, record, nloc: int, complexity: int, token_count: int):
    out_payloads = analyzer.analyze(record)
    metrics = out_payloads[0]['metrics']
    assert metrics['nloc'] == nloc
    assert metrics['complexity'] == complexity
    assert metrics['token_count'] == token_count


