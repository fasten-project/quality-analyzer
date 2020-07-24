import argparse
from fasten.plugins.kafka import KafkaPlugin
from rapidplugin.domain.package import Package


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
           1. extract package info from Kafka topic 'fasten.repoCloner.out'
           2. get the link of source code
           3. calculate quality metrics
           4. send to Kafka topic 'fasten.RapidPlugin.out (err, log)'
        """

    def consume(self, record):
        # print(record)
        # message = self.create_message(record, {"status": "begin"})
        # self.emit_message(self.log_topic, message, "begin", "")
        forge = "mvn"
        product = record['groupId']+":"+record['artifactId']
        version = record['version']
        path = record['repoPath']
        package = Package(forge, product, version, path)
        message = self.create_message(record, {"status": "begin"})
        self.emit_message(self.log_topic, message, "begin", "")
        metrics = {
            "nloc": package.nloc(),
            "method_count": package.method_count(),
            "complexity": package.complexity(),
            "file_list": [f.metrics() for f in package.files()],
            # "function_list": [fun.metrics() for fun in package.functions()]
        }
        payload = {
            "product": product,
            "forge": "mvn",
            "generator": "Lizard",
            "metrics": metrics
        }
        out_message = self.create_message(record, {"payload": payload})
        self.emit_message(self.produce_topic, out_message, "succeed", "")


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


if __name__ == "__main__":
    main()
