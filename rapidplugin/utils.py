# Copyright 2022 Software Improvement Group
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

from pathlib import PurePath


class Utils:
    @staticmethod
    def validate_message(payload):
        assert 'forge' in payload, "Missing 'forge' field."
        assert 'product' in payload, "Missing 'product' field."
        assert 'version' in payload, "Missing 'version' field."
        assert 'sourcePath' in payload, "Missing 'sourcePath' field."

    @staticmethod
    def relativize_filename(filename, prefix):
        """
        Extract the relative path of the source code file.
        :param filename: absolute path included by Lizard tool,
                        e.g. '/abs_path/rel_path/d1.c'
        :param prefix: the prefix path to remove to make the path relative
        :return: filename relative to the temporal source directory,
                        e.g. 'rel_path/d1.c'
        """
        p = PurePath(filename)
        return str(p.relative_to(prefix))
