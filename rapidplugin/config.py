# Copyright 2021 Software Improvement Group
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

class Config():
    config_dict = {}
    config_name = ""

    def __init__(self, name=""):
        self.config_name = name

    def get_config_name(self):
        return self.config_name

    def add_config_value(self, var, value):
        self.config_dict[var] = value

    def update_config_value(self, var, value):
        self.add_config_value(var, value)

    def get_config_value(self, var):
        assert var in self.config_dict, "No value for key " +\
            var + " in config " + "config_name"
        return self.config_dict[var]

    def get_all_values(self):
        return self.config_dict
