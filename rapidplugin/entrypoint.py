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

import copy
import logging
import argparse
from fasten.plugins.kafka import KafkaPlugin
from rapidplugin.analysis.lizard_analyzer import LizardPackage
from rapidplugin.utils.utils import MavenUtils, KafkaUtils
from time import sleep
import kafka.errors as errors
import os

logger = logging.getLogger(__name__)


class RapidPlugin(KafkaPlugin):

    DEFAULT_CONFIG = {
        'bootstrap_servers': 'localhost',
        'produce_topic': 'fasten.RapidPlugin.callable.out',
        'log_topic': 'fasten.RapidPlugin.callable.log',
        'err_topic': 'fasten.RapidPlugin.callable.err',
        'group_id': 'rapid-plugin',
        'sleep_time': 1,
        'base_dir': 'src',
        'analyzer': 'lizard'
    }

    def __init__(self, *topics, **configs):
        extra_configs = set(configs).difference(self.DEFAULT_CONFIG)
        if extra_configs:
            raise errors.KafkaConfigurationError("Unrecognized configs: %s" % (extra_configs,))
        self.config = copy.copy(self.DEFAULT_CONFIG)
        self.config.update(configs)
        self.consume_topics = set(topics)
        self.produce_topic = self.config['produce_topic']
        self.log_topic = self.config['log_topic']
        self.error_topic = self.config['err_topic']
        self.group_id = self.config['group_id']
        self.sleep_time = self.config['sleep_time']
        self.base_dir = self.config['base_dir']
        super().__init__(self.config['bootstrap_servers'])
        self.set_consumer()
        self.set_producer()

    def name(self):
        return "RapidPlugin"

    def description(self):
        return "A FASTEN plug-in to populate risk related metadata for a product."

    def version(self):
        return "0.0.1"

    def free_resource(self):
        pass

    """
    consume topic: 
    """
    def consume(self, record):
        payload = record['payload'] if 'payload' in record else record
        in_payload = KafkaUtils.tailor_input(payload)
        try:
            KafkaUtils.validate_message(payload)
        except AssertionError as e:
            log_message = self.create_message(in_payload, {"Status": "FAILED"})
            self.emit_message(self.log_topic, log_message, "[FAILED]", "Parsing json failed.")
            err_message = self.create_message(in_payload, {"Err": "Missing JSON fields."})
            self.emit_message(self.error_topic, err_message, "[ERROR]", e)
        out_payloads = self.analyze(payload)
        for out_payload in out_payloads:
            self.produce(in_payload, out_payload)

    def analyze(self, payload):
        out_payloads = []
        forge = payload['forge']
        product = payload['groupId'] + ":" + payload['artifactId'] if forge == "mvn" else payload['product']
        version = payload['version']
        path = self._get_source_path(payload)
        package = LizardPackage(forge, product, version, path)
        for function in package.functions():
            out_payloads.append({}.update(package.metadata()).update(function.metadata().update(function.metrics())))
        if forge == "mvn":
            self._clean_up()
        return out_payloads

    def produce(self, in_payload, out_payload):
        try:
            out_message = self.create_message(in_payload, {"payload": out_payload})
            self.emit_message(self.produce_topic, out_message, "succeed", "")
        except errors.KafkaError as e:
            log_message = self.create_message(in_payload, {"Status": "FAILED"})
            self.emit_message(self.log_topic, log_message, "[FAILED]", "Sending message failed.")
            err_message = self.create_message(in_payload, {"Err": "Message commit error."})
            self.emit_message(self.error_topic, err_message, "[ERROR]", e)

    """
    the order to get source code path from different sources: 
       [x] 1. if *-sources.jar is valid, download(get from cache), uncompress and return the path
       [ ] 2. else if repoPath is not empty
        [ ] 2.1 if commit tag is valid, checkout based on tag and return the path
       3. else return null
    """
    def _get_source_path(self, payload):
        if payload['forge'] == "mvn":
            if 'sourcesUrl' in payload:
                sources_url = payload['sourcesUrl']
                return MavenUtils.download_jar(sources_url, self.base_dir)
            else:
                if 'repoPath' in payload and 'commitTag' in payload and 'repoType' in payload:
                    repo_path = payload['repoPath']
                    repo_type = payload['repoType']
                    commit_tag = payload['commitTag']
                    return MavenUtils.checkout_version(repo_path, repo_type, commit_tag)
        else:
            return payload['sourcePath']

    def _clean_up(self):
        # delete all under base_dir
        pass


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


def main():
    parser = get_parser()
    args = parser.parse_args()
    # TODO: parsing
    plugin = RapidPlugin()

    # Run forever
    while True:
        plugin.consume_messages()
        sleep(1)


if __name__ == "__main__":
    main()
