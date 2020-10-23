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

import sys
import pytest
import rapidplugin.entrypoint as entrypoint
from rapidplugin.rapid_plugin import RapidPlugin
from rapidplugin.tests.sources import sources
from rapidplugin.tests.sources import fix_sourcePath
from rapidplugin.config import Config


@pytest.mark.parametrize('message', [
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
#     "sourcesUrl": "maven/m1/m1.jar",
#     "repoPath": "",
#     "repoType": "",
#     "commitTag": ""
# },
{
    "forge": "mvn",
    "groupId": "test-mvn",
    "artifactId": "m1",
    "version": "1.0.0",
    "sourcesUrl": "",
    "repoPath": "maven/git/m1",
    "repoType": "git",
    "commitTag": "1.0.0"
},
{
    "forge": "mvn",
    "groupId": "test-mvn",
    "artifactId": "m2",
    "version": "1.0.0",
    "sourcesUrl": "",
    "repoPath": "maven/svn/m2",
    "repoType": "svn",
    "commitTag": "1.0.0"
},
{
    "forge": "mvn",
    "groupId": "test-mvn",
    "artifactId": "m3",
    "version": "1.0.0",
    "sourcesUrl": "",
    "repoPath": "maven/hg/m3",
    "repoType": "hg",
    "commitTag": "1.0.0"
},
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
def test_consume_messages_successes(message, sources, capsys):
    run_plugin(message, sources)
    out, err = capsys.readouterr()
    assert "FAILURE" not in out
    assert "ERROR" not in out


@pytest.mark.parametrize('message', [
{
    "groupId": "ai.api",
    "artifactId": "libai",
    "version": "1.6.12",
    "repoPath": "",
    "repoType": "",
    "commitTag": ""
}])
def test_consume_messages_failures(message, sources, capsys):
    run_plugin(message, sources)
    out, err = capsys.readouterr()
    assert "FAILURE" in out
    assert "ERROR" in out


def run_plugin(message_str, sources_str):
    plugin = setup_plugin(sources_str)
    fixed_message = fix_sourcePath(message_str, sources_str)
    plugin.emit_message(plugin.consume_topic, fixed_message,
                        "[TEST]", fixed_message)
    consume_one_message(plugin)
    plugin.consumer.close()


def setup_plugin(sources_dir):
    parser = entrypoint.get_args_parser()
    config = entrypoint.get_config(parser.parse_args([]))
    config.update_config_value('sources_dir', sources_dir)
    config.update_config_value('bootstrap_servers', 'localhost:9092')
    return RapidPlugin('RapidPlugin', 'TEST', 'TEST', config)


def consume_one_message(plugin):
    for message in plugin.consumer:
            plugin.consumer.commit()
            record = message.value
            plugin.consume(record)
            break
