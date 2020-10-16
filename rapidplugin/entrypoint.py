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
import argparse
from time import sleep
from rapidplugin.rapid_plugin import RapidPlugin
from rapidplugin.config import Config

logger = logging.getLogger(__name__)

def get_parser():
    # TODO: modify argument parsing
    parser = argparse.ArgumentParser(
        "RAPID consumer"
    )
    parser.add_argument('in_topic', type=str, help="Kafka topic to read from.")
    parser.add_argument('out_topic', type=str, help="Kafka topic to write to.")
    parser.add_argument('err_topic', type=str, help="Kafka topic to write errors to.")
    parser.add_argument('log_topic', type=str, help="Kafka topic to write logs to.")
    parser.add_argument('bootstrap_servers', type=str, help="Kafka servers, comma separated.")
    parser.add_argument('group', type=str, help="Kafka consumer group to which the consumer belongs.")
    parser.add_argument('sleep_time', type=int, help="Time to sleep in between each scrape (in sec).")
    parser.add_argument('base_dir', type=str, help="Base directory for temporary store downloaded source code.")
    return parser

def default_configs():
    c = Config()
    c.add_config_value('name', 'RapidPlugin')
    c.add_config_value('description', 'A FASTEN plug-in to populate risk related metadata for a product.')
    c.add_config_value('version', '0.0.1')
    c.add_config_value('bootstrap_servers', 'localhost')
    c.add_config_value('consume_topic', 'fasten.RepoCloner.out')
    c.add_config_value('produce_topic', 'fasten.RapidPlugin.callable.out')
    c.add_config_value('err_topic', 'fasten.RapidPlugin.callable.err')
    c.add_config_value('group_id', 'rapid-plugin')
    c.add_config_value('sleep_time', '1')
    c.add_config_value('base_dir', 'src')
    return c

def main():
    parser = get_parser()
    args = parser.parse_args()
    config = default_configs()
    # TODO: add command line arguments to config
    plugin = RapidPlugin(config)

    # To run an instance that listens to a different topic, we can do:
    # config_python = default_configs()
    # config_python.add_config_value('consume_topic', 'fasten.pycg.with_sources.out')
    # plugin_python = RapidPlugin(config)
    # Or we use the coomand line args

    # Run forever
    while True:
        plugin.consume_messages()
        sleep(config.get_config_value('sleep_time'))

if __name__ == "__main__":
    main()
