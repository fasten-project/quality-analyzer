import argparse
from fasten.plugins.kafka import KafkaPlugin
from domain.package import Package
from time import sleep


class RapidPlugin(KafkaPlugin):

    def __init__(self, bootstrap_servers, consume_topic, produce_topic,
                 log_topic, error_topic, group_id):
        super().__init__(bootstrap_servers)
        self.consume_topic = consume_topic  # fasten.RepoCloner.out
        self.produce_topic = produce_topic  # fasten.RapidPlugin.out
        self.log_topic = log_topic      # fasten.RapidPlugin.err
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
           1. extract package info from Kafka topic 'fasten.repoCloner.out'
           2. get the link of source code
           3. calculate quality metrics
           4. send to Kafka topic 'fasten.RapidPlugin.out (err, log)'
        """

    def consume(self, record):
        forge = "mvn"
        payload = record['payload'] if 'payload' in record else record
        self.emit_message(self.log_topic, payload, "debug", "")
        try:
            assert 'groupId' in payload
            assert 'artifactId' in payload
            assert 'version' in payload
            product = payload['groupId'] + "." + payload['artifactId']
            group = payload['groupId']
            artifact = payload['artifactId']
            version = payload['version']
            path = self.get_source_path(payload)
            package = Package(forge, product, version, path)
            message = self.create_message(record, {"status": "begin"})
            self.emit_message(self.log_topic, message, "begin", "")
            payload = {
                "forge": forge,
                "groupId": group,
                "artifactId": artifact,
                "version": version,
                "generator": "Lizard",
                "metrics": package.metrics()
            }
            out_message = self.create_message(record, {"payload": payload})
            self.emit_message(self.produce_topic, out_message, "succeed", "")
        except AssertionError as e:
            log_message = self.create_message(record, {"status": "failed"})
            self.emit_message(self.log_topic, log_message, "failed", "Parsing json failed.")
            err_message = self.create_message(record, {"err": "Key 'groupId', 'artifactId', or 'version' not found."})
            self.emit_message(self.error_topic, err_message, "error", "Json format error.")


        """
        the order to get source code path from different sources: 
           1. if *-sources.jar is valid, download(get from cache), uncompress and return the path
           2. else if repoPath is not empty
            2.1 if commit tag is valid, checkout based on tag and return the path
            2.2 else check out nearest commit to the release date and return the path
           3. else return null
        """
    def get_source_path(self, payload):
        sourcesUrl = payload['sourcesUrl'] if 'sourcesUrl' in payload else ""
        path = payload['repoPath'] if 'repoPath' in payload else ""
        return path


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
        sleep(sleep_time)


if __name__ == "__main__":
    main()
