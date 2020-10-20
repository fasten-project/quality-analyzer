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

from fasten.plugins.kafka import KafkaPlugin
import kafka.errors as errors
from analysis.lizard_analyzer import LizardAnalyzer
from utils.utils import MavenUtils, KafkaUtils


class RapidPlugin(KafkaPlugin):
    '''
    This main class handles consuming from Kafka, executing code analysis, 
    and producing the resulting payload back into a Kafka topic.
    '''

    def __init__(self, name, version, description, plugin_config):
        self._name = name
        self._version = version
        self._description = description
        self.plugin_config = plugin_config
        super().__init__(self.plugin_config.get_config_value('bootstrap_servers'))
        self.consume_topic = self.plugin_config.get_config_value('consume_topic')
        self.produce_topic = self.plugin_config.get_config_value('produce_topic')
        self.log_topic = self.plugin_config.get_config_value('log_topic')
        self.error_topic = self.plugin_config.get_config_value('err_topic')
        self.group_id = self.plugin_config.get_config_value('group_id')
        self.sources_dir = self.plugin_config.get_config_value('sources_dir')
        self.set_consumer()
        self.set_producer()
        self.announce()

    def name(self):
        return self._name

    def version(self):
        return self._version
    
    def description(self):
        return self._description
    
    def free_resource(self):
        pass

    def announce(self):
        '''
        Announces the activation of this plugin instance to the log_topic.
        '''
        msg = self.create_message("Plugin active with configuration " +
                                  "'" + self.plugin_config.get_config_name() + "': "+
                                  format(self.plugin_config.get_all_values()),
                                  "")
        self.emit_message(self.log_topic, msg, "[BEGIN]", msg)
    
    def consume(self, record):
        '''
        TODO
        '''
        payload = record['payload'] if 'payload' in record else record
        in_payload = KafkaUtils.tailor_input(payload)
        try:
            KafkaUtils.validate_message(payload)
        except AssertionError as e:
            log_message = self.create_message(in_payload, {"Status": "FAILED"})
            self.emit_message(self.log_topic, log_message,
                              "[FAILED]", "Parsing json failed.")
            err_message = self.create_message(in_payload, {"Err": "Missing JSON fields."})
            self.emit_message(self.error_topic, err_message, "[ERROR]", e)
        analyzer = LizardAnalyzer(self.sources_dir)
        out_payloads = analyzer.analyze(payload)
        for out_payload in out_payloads:
            self.produce(in_payload, out_payload)

    def produce(self, in_payload, out_payload):
        '''
        TODO
        '''
        try:
            out_message = self.create_message(in_payload, {"payload": out_payload})
            self.emit_message(self.produce_topic, out_message, "succeed", "")
        except errors.KafkaError as e:
            log_message = self.create_message(in_payload, {"Status": "FAILED"})
            self.emit_message(self.log_topic, log_message, "[FAILED]", "Sending message failed.")
            err_message = self.create_message(in_payload, {"Err": "Message commit error."})
            self.emit_message(self.error_topic, err_message, "[ERROR]", e)


