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
import rapidplugin.entrypoint as entrypoint
from rapidplugin.rapid_plugin import RapidPlugin
from rapidplugin.integration_tests.mocks import MockConsumer
from rapidplugin.integration_tests.mocks import MockProducer
from rapidplugin.tests.sources import sources
from rapidplugin.tests.sources import fix_sourcePath


@pytest.fixture(scope='session')
def config(sources):
    parser = entrypoint.get_args_parser()
    config = entrypoint.get_config(parser.parse_args([]))
    config.update_config_value('sources_dir', str(sources))
    config.update_config_value('bootstrap_servers', 'localhost:9092')
    config.update_config_value('group_id', 'RapidPlugin-TEST')
    config.update_config_value('consumer_timeout_ms', 500)
    yield config


@pytest.fixture()
def plugin(config):
    plugin = RapidPlugin('RapidPlugin', 'TEST', 'TEST', config)
    yield plugin
    plugin.free_resource()


@pytest.fixture()
def mock_in(config):
    mock = MockProducer(config.get_config_value('bootstrap_servers'),
                        config.get_config_value('consume_topic'))
    yield mock
    mock.free_resource()


@pytest.fixture()
def mock_out(config):
    mock = MockConsumer('MockConsumerOut',
                        config.get_config_value('bootstrap_servers'),
                        config.get_config_value('produce_topic'),
                        config.get_config_value('consumer_timeout_ms'))
    mock.skip_messages()
    yield mock
    mock.free_resource()


@pytest.fixture()
def mock_log(config):
    mock = MockConsumer('MockConsumerLog',
                        config.get_config_value('bootstrap_servers'),
                        config.get_config_value('log_topic'),
                        config.get_config_value('consumer_timeout_ms'))
    mock.skip_messages()
    yield mock
    mock.free_resource()


@pytest.fixture()
def mock_err(config):
    mock = MockConsumer('MockConsumerErr',
                        config.get_config_value('bootstrap_servers'),
                        config.get_config_value('err_topic'),
                        config.get_config_value('consumer_timeout_ms'))
    mock.skip_messages()
    yield mock
    mock.free_resource()


@pytest.fixture()
def plugin_run(plugin, config, mock_in, mock_out, mock_log, mock_err,
               in_message):
    fixed_in_message = fix_sourcePath(in_message,
                                      config.get_config_value('sources_dir'))
    mock_in.emit_message(mock_in.produce_topic, fixed_in_message,
                         "[TEST]", fixed_in_message)
    plugin.consume_messages()
    mock_out.consume_messages()
    mock_log.consume_messages()
    mock_err.consume_messages()
    yield mock_out.messages, mock_log.messages, mock_err.messages,


@pytest.mark.parametrize('in_message', [
    {
        "forge": "mvn",
        "groupId": "ai.api",
        "artifactId": "libai",
        "version": "1.6.12",
        "sourcesUrl": "https://repo1.maven.org/maven2/ai/api/libai/1.6.12/libai-1.6.12-sources.jar",
        "repoPath": "",
        "repoType": "",
        "commitTag": ""
    },
    # {
    #     "forge": "mvn",
    #     "groupId": "test-mvn",
    #     "artifactId": "m1",
    #     "version": "1.0.0",
    #     "sourcesUrl": "",
    #     "repoPath": "maven/git/m1",
    #     "repoType": "git",
    #     "commitTag": "1.0.0"
    # },
    # {
    #     "forge": "mvn",
    #     "groupId": "test-mvn",
    #     "artifactId": "m2",
    #     "version": "1.0.0",
    #     "sourcesUrl": "",
    #     "repoPath": "maven/svn/m2",
    #     "repoType": "svn",
    #     "commitTag": "1.0.0"
    # },
    # {
    #     "forge": "mvn",
    #     "groupId": "test-mvn",
    #     "artifactId": "m3",
    #     "version": "1.0.0",
    #     "sourcesUrl": "",
    #     "repoPath": "maven/hg/m3",
    #     "repoType": "hg",
    #     "commitTag": "1.0.0"
    # },
    {
        "forge": "debian",
        "product": "d1",
        "version": "1.0.0",
        "sourcePath": "debian/d1"
    },
    {
        "forge": "PyPI",
        "product": "p1",
        "version": "1.0.0",
        "sourcePath": "pypi/p1"
    }])
def test_successes(plugin_run, in_message):
    out, log, err = plugin_run
    assert len(out) >= 1
    assert len(log) >= 1
    assert len(err) == 0


@pytest.mark.parametrize('in_message', [
    {
        "groupId": "ai.api",
        "artifactId": "libai",
        "version": "1.6.12",
        "repoPath": "",
        "repoType": "",
        "commitTag": ""
    },
    {
        "forge": "PyPI",
        "product": "p1",
        "version": "1.0.0"
    }])
def test_failures(plugin_run, in_message):
    out, log, err = plugin_run
    assert len(out) == 0
    assert len(log) >= 1
    assert len(err) >= 1
