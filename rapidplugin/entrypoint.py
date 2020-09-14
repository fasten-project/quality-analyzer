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
from fasten.plugins.kafka import KafkaPlugin
from domain.package import Package
from time import sleep
from kafka import KafkaProducer
import kafka.errors as Errors
from zipfile import ZipFile
import requests
import os

logger = logging.getLogger(__name__)


class RapidPlugin(KafkaPlugin):

    def __init__(self, bootstrap_servers, consume_topic, produce_topic,
                 log_topic, error_topic, group_id, sleep_time, base_dir):
        super().__init__(bootstrap_servers)
        self.consume_topic = consume_topic  # fasten.RepoCloner.out
        self.produce_topic = produce_topic  # fasten.RapidPlugin.out
        self.log_topic = log_topic      # fasten.RapidPlugin.err
        self.error_topic = error_topic  # fasten.RapidPlugin.err
        self.group_id = group_id
        self.sleep_time = sleep_time
        self.base_dir = base_dir
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
           1. extract package info from Kafka topic 'fasten.repoCloner.out'
           2. get the link of source code
           3. calculate quality metrics
           4. send to Kafka topic 'fasten.RapidPlugin.out (err, log)'
        """

    def consume(self, record):
        forge = "mvn"
        payload = record['payload'] if 'payload' in record else record
        try:
            assert 'groupId' in payload
            assert 'artifactId' in payload
            assert 'version' in payload
            product = payload['groupId'] + "." + payload['artifactId']
            group = payload['groupId']
            artifact = payload['artifactId']
            version = payload['version']
            path = self._get_source_path(payload)
            package = Package(forge, product, version, path)
            message = self.create_message(record, {"Status": "Begin"})
            self.emit_message(self.log_topic, message, "Begin", payload)
            payload = {
                "forge": forge,
                "groupId": group,
                "artifactId": artifact,
                "version": version,
                "generator": "Lizard",
                "metrics": package.metrics()
            }
            out_message = self.create_message(record, {"payload": payload})
            self.emit_message(self.produce_topic, out_message, "succeed", out_message['payload'])
        except AssertionError as e:
            log_message = self.create_message(record, {"Status": "FAILED"})
            self.emit_message(self.log_topic, log_message, "[FAILED]", "Parsing json failed.")
            err_message = self.create_message(record, {"Err": "Key 'groupId', 'artifactId', or 'version' not found."})
            self.emit_message(self.error_topic, err_message, "[ERROR]", "Json format error.")
        except Errors.BrokerResponseError as e:
            log_message = self.create_message(record, {"Status": "FAILED"})
            self.emit_message(self.log_topic, log_message, "[FAILED]", "Sending message failed.")
            err_message = self.create_message(record, {"Err": "Message too large."})
            self.emit_message(self.error_topic, err_message, "[ERROR]", "MessageSizeTooLargeError.")

    def set_producer(self):
        """Set producer to sent messages to produce_topic.
        """
        try:
            assert self.produce_topic is not None
            assert self.bootstrap_servers is not None
        except (AssertionError, NameError) as e:
            self.err("You should have set produce_topic, bootstrap_servers, ")
            raise e
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers.split(','),
            max_request_size=15728640,
            value_serializer=lambda x: x.encode('utf-8')
        )

        """
        the order to get source code path from different sources: 
           [x] 1. if *-sources.jar is valid, download(get from cache), uncompress and return the path
           [ ] 2. else if repoPath is not empty
            [ ] 2.1 if commit tag is valid, checkout based on tag and return the path
            [ ] 2.2 else check out nearest commit to the release date and return the path
           3. else return null
        """
    def _get_source_path(self, payload):
        sources_url = payload['sourcesUrl'] if 'sourcesUrl' in payload else ""
        path = self._download_jar(sources_url) if sources_url != "" else ""
        if path == "":
            path = payload['repoPath'] if 'repoPath' in payload else ""
        return path

    def _download_jar(self, url):
        if not self.base_dir.exists():
            self.base_dir.mkdir(parents=True)
        file_name = self.base_dir/url.split('/')[-1]
        tmp_dir = self.base_dir/'tmp'
        r = requests.get(url, allow_redirects=True)
        open(file_name, 'wb').write(r.content)
        with ZipFile(file_name, 'r') as zipObj:
            zipObj.extractall(tmp_dir)
        # delete jar file
        return tmp_dir

    def _checkout_version(self, repo_path):
        pass


def get_parser():
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

    in_topic = args.in_topic
    out_topic = args.out_topic
    err_topic = args.err_topic
    log_topic = args.log_topic
    bootstrap_servers = args.bootstrap_servers
    group = args.group
    sleep_time = args.sleep_time
    base_dir = args.base_dir

    plugin = RapidPlugin(bootstrap_servers, in_topic, out_topic, log_topic,
                         err_topic, group, sleep_time, base_dir)

    # Run forever
    while True:
        plugin.consume_messages()
        sleep(sleep_time)


if __name__ == "__main__":
    main()
