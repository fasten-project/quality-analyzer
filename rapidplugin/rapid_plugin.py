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
from analysis.lizard_analyzer import LizardPackage
from utils.utils import MavenUtils, KafkaUtils

class RapidPlugin(KafkaPlugin):
    '''
    This main class handles consuming from Kafka, executing code analysis, 
    and producing the resulting payload back into a Kafka topic.
    '''

    def __init__(self, config):
        self.config = config
        super().__init__(self.config.get_config_value('bootstrap_servers'))
        self.consume_topic = self.config.get_config_value('consume_topic')
        self.produce_topic = self.config.get_config_value('produce_topic')
        self.log_topic = self.config.get_config_value('log_topic')
        self.error_topic = self.config.get_config_value('err_topic')
        self.group_id = self.config.get_config_value('group_id')
        self.base_dir = self.config.get_config_value('base_dir')
        self.set_consumer()
        self.set_producer()

    def name(self):
        return self.config.get_config_value('name')

    def description(self):
        return self.config.get_config_value('description')

    def version(self):
        return self.config.get_config_value('version')

    def free_resource(self):
        pass

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
        out_payloads = self.analyze(payload)
        for out_payload in out_payloads:
            self.produce(in_payload, out_payload)

    def analyze(self, payload):
        '''
        TODO
        '''
        out_payloads = []
        forge = payload['forge']
        group_id = payload['groupId']
        artifact_id = payload['artifactId']
        product = group_id + ":" + artifact_id if forge == "mvn" else payload['product']
        version = payload['version']
        path = self._get_source_path(payload)
        package = LizardPackage(forge, product, version, path)
        for function in package.functions():
            out_payloads.append({}.
                                update(package.metadata()).
                                update(function.metadata().
                                       update(function.metrics())))
        if forge == "mvn":
            self._clean_up()
        return out_payloads

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

    def _get_source_path(self, payload):
        """
        TODO: consider moving this to a utility class.
        the order to get source code path from different sources: 
        [x] 1. if *-sources.jar is valid, download(get from cache), 
               uncompress and return the path
        [ ] 2. else if repoPath is not empty
        [ ] 2.1 if commit tag is valid, checkout based on tag and return the path
            3. else return null
        """
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
        '''
        TODO: delete all under base_dir
        '''
