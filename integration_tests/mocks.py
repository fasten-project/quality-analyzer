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

from fasten.plugins.kafka import KafkaPlugin
from rapidplugin.kafka_non_blocking import KafkaPluginNonBlocking


class MockConsumer(KafkaPluginNonBlocking):
    def __init__(self, group_id, bootstrap_servers, consume_topic):
        super().__init__(bootstrap_servers)
        self.group_id = group_id
        self.consume_topic = consume_topic
        self.consumer_timeout_ms = 1000
        self.set_consumer()
        self.messages = []

    def name(self):
        return "MockConsumer"

    def version(self):
        return "TEST"

    def description(self):
        return "TEST"

    def consume(self, record):
        self.messages.append(record)

    def free_resource(self):
        if self.consumer is not None:
            self.consumer.close()


class MockProducer(KafkaPlugin):
    def __init__(self, bootstrap_servers, produce_topic):
        super().__init__(bootstrap_servers)
        self.produce_topic = produce_topic
        self.set_producer()

    def name(self):
        return "MockProducer"

    def version(self):
        return "TEST"

    def description(self):
        return "TEST"

    def consume(self, record):
        pass

    def free_resource(self):
        if self.producer is not None:
            self.producer.close()
