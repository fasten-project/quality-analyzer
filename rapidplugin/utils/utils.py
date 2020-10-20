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

from zipfile import ZipFile
from pathlib import Path
from git import Repo
from threading import Lock
import requests


class MavenUtils:

    # TODO:add exception handling
    @staticmethod
    def download_jar(url, base_dir):
        if url == "":
            return ""
        else:
            base_dir = Path(base_dir)
            if not base_dir.exists():
                base_dir.mkdir(parents=True)
            file_name = base_dir/url.split('/')[-1]
            tmp_dir = base_dir/"tmp"
            r = requests.get(url, allow_redirects=True)
            open(file_name, 'wb').write(r.content)
            with ZipFile(file_name, 'r') as zipObj:
                zipObj.extractall(tmp_dir)
            # TODO: delete jar file
            return tmp_dir

    @staticmethod
    def checkout_version(repo_path, repo_type, version_tag, base_dir):
        base_dir = Path(base_dir)
        if not base_dir.exists():
            base_dir.mkdir(parents=True)
        if repo_type == "git":
            # check out
            return base_dir/repo_path
        else:
            return ""


class KafkaUtils:
    @staticmethod
    def validate_message(payload):
        assert 'forge' in payload, "Missing 'forge' field."
        forge = payload['forge']
        assert forge in {"mvn", "debian", "PyPI"}, "Unknown forge: '{}}'.".format(forge)
        if forge == "mvn":
            assert 'groupId' in payload, "Missing 'groupId' field."
            assert 'artifactId' in payload, "Missing 'artifactId' field."
            assert 'version' in payload, "Missing 'version' field."
        else:
            assert 'product' in payload, "Missing 'product' field."
            assert 'version' in payload, "Missing 'version' field."

    @staticmethod
    def tailor_input(payload):
        """
        Tailor 'payload' from consumed topics,
        to avoid (big) call graph data
        adding to 'input' field in the produced topics.
        """
        graph = {
            "graph": {}
        }
        modules = {
            "modules": {}
        }
        cha = {
            "cha": {}
        }
        if 'graph' in payload:
            payload.update(graph)
        if 'modules' in payload:
            payload.update(modules)
        if 'cha' in payload:
            payload.update(cha)
        return payload


