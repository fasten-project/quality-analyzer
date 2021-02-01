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

import datetime
import textwrap
from time import sleep
from fasten.plugins.kafka import KafkaPluginNonBlocking
from rapidplugin.analysis.lizard_analyzer import LizardAnalyzer
from rapidplugin.utils.utils import KafkaUtils


class RapidPlugin(KafkaPluginNonBlocking):
    '''
    This main class handles consuming and producing from/to Kafka.
    Code analysis is executed for the supported payloads.
    '''

    def __init__(self, name, version, description, plugin_config):
        self._name = name
        self._version = version
        self._description = description
        self.plugin_config = plugin_config
        super().__init__(self.plugin_config.get_config_value('bootstrap_servers'))
        self.consume_topic = self.plugin_config.get_config_value('consume_topic')
        self.produce_topic = self.plugin_config.get_config_value('produce_topic')
        self.produce_callable_topic = self.plugin_config.get_config_value('produce_callable_topic')
        self.log_topic = self.plugin_config.get_config_value('log_topic')
        self.error_topic = self.plugin_config.get_config_value('err_topic')
        self.group_id = self.plugin_config.get_config_value('group_id')
        self.sources_dir = self.plugin_config.get_config_value('sources_dir')
        self.consumer_timeout_ms = self.plugin_config.get_config_value('consumer_timeout_ms')
        self.consumption_delay_sec = self.plugin_config.get_config_value('consumption_delay_sec')
        self.max_log_message_width = self.plugin_config.get_config_value('max_log_message_width')
        self.set_consumer_with_retry()
        self.set_producer_with_retry()

    def name(self):
        return self._name

    def version(self):
        return self._version

    def description(self):
        return self._description

    def run_forever(self):
        self.announce_activation()
        try:
            while True:
                # self.announce_heartbeat()
                self.flush_logs()
                sleep(self.consumption_delay_sec)
                try:
                    self.consume_messages()
                except BaseException as e:
                    self.handle_failure({}, 'Fatal exception while consuming.', e)
                    raise e
        finally:
            self.announce_termination()
            self.free_resource()

    def announce_activation(self):
        '''
        Announces the activation of this plugin instance to the log_topic.
        '''
        self.handle_success(format(
            self.plugin_config.get_all_values()),
                         "Plugin activated with configuration " +
                         "'" + self.plugin_config.get_config_name() + "'")

    def announce_heartbeat(self):
        '''
        Announces a heartbeat of the running plugin to the log_topic.
        '''
        self.handle_success(format(
            self.plugin_config.get_all_values()),
                         "Plugin heartbeat with configuration " +
                         "'" + self.plugin_config.get_config_name() + "'")

    def announce_termination(self):
        '''
        Announces the termination of this plugin instance to the log_topic.
        '''
        self.handle_success(format(
            self.plugin_config.get_all_values()),
                         "Plugin terminated with configuration " +
                         "'" + self.plugin_config.get_config_name() + "'")

    def consume(self, record):
        '''
        Call-back method to handle a message on self.consume_topic.
        Parses the payload and passes on to the self.produce method for
        processing the provided coordinates.

        Arguments:
          record (JSON): message from self.consume_topic
        '''
        record = KafkaUtils.extract_from_metadata_db_ext_topic(record)
        payload = record['payload'] if 'payload' in record else record
        in_payload = KafkaUtils.tailor_input(payload)
        try:
            KafkaUtils.validate_message(payload)
            self.handle_success(in_payload, "Consumed message successfully.")
            self.produce(in_payload)
        except Exception as e:
            self.handle_failure(in_payload, "Consume failed for message.",
                                str(e))

    def produce(self, in_payload):
        '''
        Produces quality analysis results to the produce_topics. A separate
        message will be emitted for each payload generated by the analyzer.

        Arguments:
          in_payload (JSON): validated source code location
        '''
        try:
            analyzer = LizardAnalyzer(self.sources_dir)
            out_payloads = analyzer.analyze(in_payload)
            self.produce_revision(in_payload, out_payloads)
            self.handle_success(in_payload,
                                "Quality analysis results produced.")
        except Exception as e:
            self.handle_failure(in_payload,
                                "Quality analysis failed for payload.", str(e))

    def produce_revision(self, in_payload, out_payloads):
        for out_payload in out_payloads:
                self.produce_callable(in_payload, out_payload)
        out_message = self.create_message(in_payload, {"callables_produced": len(out_payloads)})
        self.emit_message(self.produce_topic, out_message, "[SUCCESS]", out_message)

    def produce_callable(self, in_payload, out_payload):
        out_message = self.create_message(in_payload, {"payload": out_payload})
        self.emit_message(self.produce_callable_topic, out_message, "[SUCCESS]",
                          out_message)

    def handle_failure(self, in_payload, failure, error):
        '''
        Log a failure and the underlying error to the appropriate topics and to
        stderr.

        Arguments:
          in_payload (JSON): The payload for which the failure occurred.
          failure (str)    : Description of what failed.
          error (str)      : Description of the underlying error (exception).
        '''
        err_message = self.create_message(in_payload, {"error": error})
        self.err(err_message)
        self.emit_message(self.error_topic, err_message, "[ERROR]",
                          err_message)
        log_message = self.create_message(in_payload, {"status": "FAILURE",
                                                       "failure": failure})
        self.emit_message(self.log_topic, log_message, "[FAILURE]",
                          log_message)

    def handle_success(self, in_payload, success):
        '''
        Log a success to the appropriate topics.

        Arguments:
          in_payload (JSON): The payload for which the success occurred.
        '''
        log_message = self.create_message(in_payload, {"status": "SUCCESS",
                                                       "success": success})
        self.emit_message(self.log_topic, log_message, "[SUCCESS]",
                          log_message)

    def log(self, message):
        super().log("{}: {}".format(
            str(datetime.datetime.now()), textwrap.shorten(message, width=self.max_log_message_width)
        ))

    def err(self, error):
        super().err("{}: {}".format(
            str(datetime.datetime.now()), error
        ))

    def flush_logs(self):
        self.logs.flush()
        self.errors.flush()

    def free_resource(self):
        try:
            if self.consumer is not None:
                self.consumer.close()
            if self.producer is not None:
                self.producer.close()
        except BaseException as e:
            self.err('Fatal exception while freeing resources: ' + str(e))
            raise e
        else:
            self.log('Resources freed successfully.')
