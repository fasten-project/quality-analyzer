# Copyright 2022 Software Improvement Group
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
from rapidplugin.tests.sources import fix_sourcePath
from rapidplugin.lizard_analyzer import LizardAnalyzer
from rapidplugin.tests.sources import sources


@pytest.fixture(scope='session')
def analyzer(sources):
    yield LizardAnalyzer(str(sources))


java_message = {
    "forge": "mvn",
    "product": "m1",
    "version": "1.0.0",
    "sourcePath": "maven/m1"
}
c_message = {
    "forge": "debian",
    "product": "d1",
    "version": "1.0.0",
    "sourcePath": "debian/d1"
}
python_message = {
    "forge": "PyPI",
    "product": "p1",
    "version": "1.0.0",
    "sourcePath": "pypi/p1"
}

# List of (payload, function_count) pairs
FUNCTION_COUNT_DATA = [
    (java_message, 1),
    (c_message, 1),
    (python_message, 1)
]

# List of (payload, start_line, end_line) tuples
FUNCTION_LINE_DATA = [
    (java_message, 2, 4),
    (c_message, 3, 3),
    (python_message, 1, 2)
]

# List of (payload, nloc, complexity, token_count, parameter_count) tuples
FUNCTION_METRICS_DATA = [
    (java_message, 3, 1, 16, 1),
    (c_message, 1, 1, 5, 0),
    (python_message, 2, 1, 5, 0)
]

# List of (payload, filename) pairs
FUNCTION_FILENAME_DATA = [
    (java_message, "m1.java"),
    (c_message, "d1.c"),
    (python_message, "p1.py")
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


@pytest.mark.parametrize('record,nloc,complexity,token_cnt,parameter_cnt', FUNCTION_METRICS_DATA)
def test_function_metrics(analyzer, sources, record, nloc: int, complexity: int, token_cnt: int, parameter_cnt: int):
    out_payloads = analyzer.analyze(fix_sourcePath(record, sources))
    metrics = out_payloads[0]['metrics']
    assert metrics['nloc'] == nloc
    assert metrics['complexity'] == complexity
    assert metrics['token_count'] == token_cnt
    assert metrics['parameter_count'] == parameter_cnt


@pytest.mark.parametrize('record,filename', FUNCTION_FILENAME_DATA)
def test_function_filename(analyzer, sources, record, filename):
    out_payloads = analyzer.analyze(fix_sourcePath(record, sources))
    metadata = out_payloads[0]
    assert metadata['filename'] == filename
