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
    def __init__(self, group_id, bootstrap_servers, consume_topic, consumer_timeout_ms):
        self.group_id = group_id
        self.consume_topic = consume_topic
        self.bootstrap_servers = bootstrap_servers
        self.consumer_timeout_ms = consumer_timeout_ms
        self.set_consumer()


class MockProducer(KafkaPlugin):
    def __init__(self, bootstrap_servers, produce_topic):
        self.produce_topic = produce_topic
        self.bootstrap_servers = bootstrap_servers
        self.set_producer()
