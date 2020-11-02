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
    def get_source_path(payload, base_dir):
        """
        For maven, the order to get source code path from different sources:
        [x] 1. if *-sources.jar is valid, download,
               uncompress and return the path to the source code
        [x] 2. else if repoPath is not empty, and
        [x]    2.1 if commit tag is valid, checkout based on tag and return the path
        [ ]    2.2 if needed, checkout based on the release date.
        [x] 3. else return None and raise exception (Cannot get source code)
        """
        base_dir = Path(base_dir)
        if not base_dir.exists():
            base_dir.mkdir(parents=True)
        if payload['forge'] == "mvn":
            source_path = MavenUtils.get_source_mvn(payload, base_dir)
        else:
            source_path = MavenUtils.get_source_other(payload, base_dir)
        return source_path

    @staticmethod
    def get_source_mvn(payload, base_dir):
        if 'sourcesUrl' in payload:
            sources_url = payload['sourcesUrl']
            if sources_url != "":
                return MavenUtils.download_jar(sources_url, base_dir)
            elif 'repoPath' in payload and 'commitTag' in payload and 'repoType' in payload:
                repo_path = payload['repoPath']
                repo_type = payload['repoType']
                commit_tag = payload['commitTag']
                source_path = MavenUtils.checkout_version(repo_path, repo_type, commit_tag, base_dir)
                return source_path

    @staticmethod
    def get_source_other(payload, base_dir):
        assert 'sourcePath' in payload, \
            f"Cannot get source code for '{payload['product']}:{payload['version']}', missing 'sourcePath'."
        source_path = payload['sourcePath']
        assert source_path != "", \
            f"Cannot get source code for '{payload['product']}:{payload['version']}', empty 'sourcePath."
        assert os.path.isabs(source_path), "sourcePath: '{}' is not an absolute path!".format(source_path)
        source_path = MavenUtils.copy_source(payload['sourcePath'], base_dir)
        return source_path

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
            MavenUtils.git_checkout(repo_path, version_tag, tmp_path)
        elif repo_type == "svn":
            MavenUtils.svn_checkout(repo_path, version_tag, tmp_path)
        elif repo_type == "hg":
            MavenUtils.hg_checkout(repo_path, version_tag, tmp_path)
        return tmp

    @staticmethod
    def git_checkout(repo_path, version_tag, tmp_path):
        repo = Repo(repo_path)
        assert repo.tags[version_tag] is not None, "Tag: '{}' does not exist.".format(version_tag)
        archive_name = version_tag+".zip"
        archive_file_name = tmp_path/archive_name
        repo.git.archive(version_tag, o=archive_file_name)
        with ZipFile(archive_file_name, 'r') as zipObj:
            zipObj.extractall(tmp_path)

    @staticmethod
    def svn_checkout(repo_path, version_tag, tmp_path):
        raise NotImplementedError
        # 'svn export' does not support tag
        # r = LocalClient(repo_path)
        # r.export(tmp_path, version_tag)

    @staticmethod
    def hg_checkout(repo_path, version_tag, tmp_path):
        os.chdir(repo_path)
        cmd = [
            'hg',
            'archive',
            '-r', version_tag,
            '-t', 'files',
            tmp_path
        ]
        proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
        out, err = proc.communicate()

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
        tailor = {
            "graph": {},
            "modules": {},
            "cha": {},
            "depset": [],
            "build_depset": [],
            "undeclared_depset": [],
            "functions": {}
        }
        for key in tailor.keys():
            if key in payload:
                payload[key] = tailor[key]
        return payload


