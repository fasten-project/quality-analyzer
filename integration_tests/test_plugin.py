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
from time import sleep
from integration_tests.mocks import MockConsumer
from integration_tests.mocks import MockProducer


@pytest.fixture()
def mock_in():
    mock = MockProducer('kafka:9092',
                        'fasten.SourcesProvider.out')
    yield mock
    mock.free_resource()


@pytest.fixture()
def mock_out():
    mock = MockConsumer('MockConsumerOut',
                        'kafka:9092',
                        'fasten.RapidPlugin.callable.out')
    mock.skip_messages()
    yield mock
    mock.free_resource()


@pytest.fixture()
def mock_log():
    mock = MockConsumer('MockConsumerLog',
                        'kafka:9092',
                        'fasten.RapidPlugin.log')
    mock.skip_messages()
    yield mock
    mock.free_resource()


@pytest.fixture()
def mock_err():
    mock = MockConsumer('MockConsumerErr',
                        'kafka:9092',
                        'fasten.RapidPlugin.err')
    mock.skip_messages()
    yield mock
    mock.free_resource()


@pytest.fixture()
def plugin_run(mock_in, mock_out, mock_log, mock_err,
               in_message):
    mock_in.emit_message(mock_in.produce_topic, in_message,
                         "[TEST]", in_message)
    sleep(2)
    mock_out.consume_messages()
    mock_log.consume_messages()
    mock_err.consume_messages()
    yield mock_out.messages, mock_log.messages, mock_err.messages


@pytest.mark.parametrize('in_message', [
    {
        "forge": "mvn",
        "product": "m1",
        "version": "1.0.0",
        "sourcePath": "/plugin/rapidplugin/tests/resources/maven/m1"
    },
    {
        "forge": "debian",
        "product": "d1",
        "version": "1.0.0",
        "sourcePath": "/plugin/rapidplugin/tests/resources/debian/d1"
    },
    {
        "forge": "PyPI",
        "product": "p1",
        "version": "1.0.0",
        "sourcePath": "/plugin/rapidplugin/tests/resources/pypi/p1"
    }])
def test_successes(plugin_run, in_message):
    out, log, err = plugin_run
    assert len(out) >= 1
    assert len(log) >= 1
    assert len(err) == 0


@pytest.mark.parametrize('in_message', [
    # missing 'forge'
    {
        "product": "m1",
        "version": "1.0.0",
        "sourcePath": "/plugin/rapidplugin/tests/resources/maven/m1"
    },
    # missing 'sourcePath'
    {
        "forge": "PyPI",
        "product": "p1",
        "version": "1.0.0"
    }
])
def test_failures(plugin_run, in_message):
    out, log, err = plugin_run
    assert len(out) == 0
    assert len(log) >= 1
    assert len(err) >= 1
