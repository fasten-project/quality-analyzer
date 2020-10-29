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
from svn.local import LocalClient
import requests
import subprocess as sp
from tempfile import TemporaryDirectory
import os
import shutil


class MavenUtils:

    @staticmethod
    def copy_source(source_path, base_dir):
        tmp = TemporaryDirectory(dir=base_dir)
        tmp_path = Path(tmp.name)
        shutil.copytree(source_path, tmp_path, dirs_exist_ok=True)
        return tmp

    @staticmethod
    def download_jar(url, base_dir):
        tmp = TemporaryDirectory(dir=base_dir)
        tmp_path = Path(tmp.name)
        file_name = tmp_path/url.split('/')[-1]
        r = requests.get(url, allow_redirects=True)
        open(file_name, 'wb').write(r.content)
        with ZipFile(file_name, 'r') as zipObj:
            zipObj.extractall(tmp_path)
        return tmp

    @staticmethod
    def checkout_version(repo_path, repo_type, version_tag, base_dir):
        assert repo_type in {"git", "svn", "hg"}, "Unknown repo type: '{}'.".format(repo_type)
        assert repo_path != "", "Empty repo_path."
        assert version_tag != "", "Empty version_tag."
        tmp = TemporaryDirectory(dir=base_dir)
        tmp_path = Path(tmp.name)
        if repo_type == "git":
            repo = Repo(repo_path)
            assert repo.tags[version_tag] is not None, "Tag: '{}' does not exist.".format(version_tag)
            archive_name = version_tag+".zip"
            archive_file_name = tmp_path/archive_name
            repo.git.archive(version_tag, o=archive_file_name)
            with ZipFile(archive_file_name, 'r') as zipObj:
                zipObj.extractall(tmp_path)
        elif repo_type == "svn":
            return None
            # r = LocalClient(repo_path)
            # r.export(tmp, version_tag)
        elif repo_type == "hg":
            return None
            # cmd = [
            #     'hg',
            #     'archive',
            #     '-r', version_tag,
            #     '-t', 'files',
            #     tmp
            # ]
            # proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
            # o, e = proc.communicate()
        return tmp


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
        depset = {
            "depset": []
        }
        build_depset = {
            "build_depset": []
        }
        undeclared_depset = {
            "undeclared_depset": []
        }
        functions = {
            "functions" :{}
        }
        if 'graph' in payload:
            payload.update(graph)
        if 'modules' in payload:
            payload.update(modules)
        if 'cha' in payload:
            payload.update(cha)
        if 'depset' in payload:
            payload.update(depset)
        if 'build_depset' in payload:
            payload.update(build_depset)
        if 'undeclared_depset' in payload:
            payload.update(undeclared_depset)
        if 'functions' in payload:
            payload.update(functions)
        return payload


