import argparse
import json
from zipfile import ZipFile
from fasten.plugins.kafka import KafkaPlugin
# from rapidplugin.domain.package import Package
import lizard
import lizard_languages
from pydriller import RepositoryMining


class RapidPlugin(KafkaPlugin):

    def __init__(self, bootstrap_servers, consume_topic, produce_topic,
                 log_topic, error_topic, group_id):
        super().__init__(bootstrap_servers)
        self.consume_topic = consume_topic  # fasten.RepoCloner.out
        self.produce_topic = produce_topic  # fasten.RapidPlugin.out
        self.log_topic = log_topic
        self.error_topic = error_topic  # fasten.RapidPlugin.err
        self.group_id = group_id
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
           1. extract package info, repo info write to metadata DB, 
                not Kafka topic, need to confirm.
           2. get the link from metadataDB, downloaded source code
           3. either extend fasten-python-plugin with metadataDB 
                connection or implement a java plugin to produce
                a Kafka topic with package name and link to code (assuming this)
        """

    def consume(self, record):
        message = self.create_message(record, {"status": "begin"})
        self.emit_message(self.log_topic, message, "begin", "")
        # print(record)
        # data = json.loads(record)
        # package = Package("maven", data['artifactId'], data['version'])
        # package.path = data['jarPath']
        #
        # message = self.create_message(record, {"status": "begin"})
        # self.emit_message(self.log_topic, message, "begin", "")
        # out_message = self.create_message(data)
        # self.emit_message(self.produce_topic, out_message, {"repo": package.path})

    def _unzip(self, path):
        code_path = None
        return code_path

    def _clone(self, path):
        code_path = None
        return code_path


def get_parser():
    parser = argparse.ArgumentParser(
        "RAPID consumer"
    )
    parser.add_argument('in_topic', type=str, help="Kafka topic to read from.")
    parser.add_argument(
        'out_topic',
        type=str,
        help="Kafka topic to write to."
    )
    parser.add_argument(
        'err_topic',
        type=str,
        help="Kafka topic to write errors to."
    )
    parser.add_argument(
        'log_topic',
        type=str,
        help="Kafka topic to write logs to."
    )
    parser.add_argument(
        'bootstrap_servers',
        type=str,
        help="Kafka servers, comma separated."
    )
    parser.add_argument(
        'group',
        type=str,
        help="Kafka consumer group to which the consumer belongs."
    )
    parser.add_argument(
        'sleep_time',
        type=int,
        help="Time to sleep in between each scrape (in sec)."
    )
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

    plugin = RapidPlugin(bootstrap_servers, in_topic, out_topic, log_topic,
                         err_topic, group)

    # Run forever
    while True:
        plugin.consume_messages()


if __name__ == "__main__":
    main()
