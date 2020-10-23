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
from rapidplugin.tests.sources import sources
from rapidplugin.tests.sources import fix_sourcePath
from rapidplugin.config import Config


@pytest.fixture(scope='session')
def plugin(sources):
    parser = entrypoint.get_args_parser()
    config = entrypoint.get_config(parser.parse_args([]))
    config.update_config_value('sources_dir', sources)
    config.update_config_value('bootstrap_servers', 'localhost:9092')
    yield RapidPlugin('RapidPlugin', 'TEST', 'TEST', config)


def test_consume_messages_succesfully(plugin):
    my_plugin = plugin
    src_msg = fix_sourcePath({
        "forge": "PyPI",
        "product": "p1",
        "version": "1.0.0",
        "sourcePath": "pypi/p1"
    }, my_plugin.sources_dir)
    my_plugin.emit_message(my_plugin.consume_topic,
                           src_msg,
                           "TEST", "")
    for message in my_plugin.consumer:
            my_plugin.consumer.commit()
            record = message.value
            my_plugin.consume(record)
            break
