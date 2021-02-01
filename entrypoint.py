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
import pprint
from rapidplugin.rapid_plugin import RapidPlugin
from rapidplugin.config import Config

logger = logging.getLogger(__name__)

plugin_name = 'RapidPlugin'
plugin_description = 'A FASTEN plug-in to populate risk related metadata for a product.'
plugin_version = '1.1.3'


def get_args_parser():
    args_parser = argparse.ArgumentParser("RapidPlugin")

    args_parser.add_argument('--consume_topic', type=str,
                             default='fasten.RepoCloner.out',
                             help="Kafka topic to consume from.")

    args_parser.add_argument('--produce_topic', type=str,
                             default='fasten.RapidPlugin.callable.out',
                             help="Kafka topic to produce to.")

    args_parser.add_argument('--err_topic', type=str,
                             default='fasten.RapidPlugin.callable.err',
                             help="Kafka topic to write errors to.")

    args_parser.add_argument('--log_topic', type=str,
                             default='fasten.RapidPlugin.callable.log',
                             help="Kafka topic to write logs to.")

    args_parser.add_argument('--bootstrap_servers', type=str,
                             default='localhost',
                             help="Kafka servers, comma separated list between quotes.")

    args_parser.add_argument('--group_id', type=str,
                             default='RapidPlugin',
                             help="Kafka consumer group ID to which the consumer belongs.")

    args_parser.add_argument('--consumer_timeout_ms', type=int,
                             default=1000,
                             help="Timeout in milliseconds to consume messages from topic.")

    args_parser.add_argument('--consumption_delay_sec', type=int,
                             default=1,
                             help="Delay in seconds between each message consumption call.")

    args_parser.add_argument('--sources_dir', type=str,
                             default='src',
                             help="Base directory for temporary storing downloaded source code.")

    args_parser.add_argument('--max_log_message_width', type=int,
                             default=320,
                             help="Maximum number of characters before a log message will be truncated.")

    return args_parser


def get_config(args):
    c = Config('Default')
    c.add_config_value('bootstrap_servers', args.bootstrap_servers)
    c.add_config_value('consume_topic', args.consume_topic)
    c.add_config_value('produce_topic', args.produce_topic)
    c.add_config_value('produce_callable_topic', args.produce_callable_topic)
    c.add_config_value('err_topic', args.err_topic)
    c.add_config_value('log_topic', args.log_topic)
    c.add_config_value('group_id', args.group_id)
    c.add_config_value('consumption_delay_sec', args.consumption_delay_sec)
    c.add_config_value('consumer_timeout_ms', args.consumer_timeout_ms)
    c.add_config_value('sources_dir', args.sources_dir)
    c.add_config_value('max_log_message_width', args.max_log_message_width)
    return c


def main():
    parser = get_args_parser()
    plugin_config = get_config(parser.parse_args())

    print(plugin_name + ' ' + plugin_version)
    print('Running with configuration ' +
          '\"' + plugin_config.get_config_name() + '\"')

    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(plugin_config.get_all_values())

    plugin = RapidPlugin(plugin_name, plugin_version,
                         plugin_description, plugin_config)
    plugin.run_forever()


if __name__ == "__main__":
    main()
