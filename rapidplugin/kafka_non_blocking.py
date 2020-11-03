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


import json
from time import sleep
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from fasten.plugins.kafka import KafkaPlugin


class KafkaPluginNonBlocking(KafkaPlugin):

    consumer_timeout_ms = None

    def set_consumer(self):
        """Set consumer to read (non-blocking) from consume_topic.
        """
        try:
            assert self.consume_topic is not None
            assert self.bootstrap_servers is not None
            assert self.group_id is not None
            assert self.consumer_timeout_ms is not None
        except (AssertionError, NameError) as e:
            self.err(("You should have set consume_topic, bootstrap_servers, "
                      "group_id, and consumer_timeout_ms"))
            raise e
        self.consumer = KafkaConsumer(
            self.consume_topic,
            bootstrap_servers=self.bootstrap_servers.split(','),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            max_poll_records=1,
            group_id=self.group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=self.consumer_timeout_ms
        )

    def set_consumer_with_retry(self):
        while True:
            try:
                self.set_consumer()
                self.set_producer()
            except NoBrokersAvailable:
                self.err("Could not connect consumer to Kafka, re-trying...")
            else:
                self.log("Connected consumer to Kafka successfully.")
                break
            sleep(self.consumption_delay_sec)

    def set_producer_with_retry(self):
        while True:
            try:
                self.set_producer()
            except NoBrokersAvailable:
                self.err("Could not connect producer to Kafka, re-trying...")
            else:
                self.log("Connected producer to Kafka successfully.")
                break
            sleep(self.consumption_delay_sec)

    def skip_messages(self):
        assert self.consumer is not None, "Consumer needs to be set before messages can ben consumed."
        for m in self.consumer:
            self.consumer.commit()
