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

from zipfile import ZipFile
from pathlib import Path, PurePath
from git import Repo
from svn.local import LocalClient
import requests
import subprocess as sp
from tempfile import TemporaryDirectory
import os
import shutil
import re


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
            return MavenUtils.get_source_mvn(payload, base_dir)
        else:
            return MavenUtils.get_source_other(payload, base_dir)

    @staticmethod
    def get_source_mvn(payload, base_dir):
        source_config = {}
        if 'sourcesUrl' in payload:
            sources_url = payload['sourcesUrl']
            if sources_url != "":
                return MavenUtils.download_jar(sources_url, base_dir)
            else:
                assert 'repoType' in payload, f"Missing field 'repoType' to check out source code."
                repo_path = payload['repoPath']
                repo_type = payload['repoType']
                commit_tag = payload['commitTag']
                return MavenUtils.checkout_version(base_dir, repo_path=repo_path, repo_type=repo_type, version_tag=commit_tag)

    @staticmethod
    def get_source_other(payload, base_dir):
        assert 'sourcePath' in payload, \
            f"Cannot get source code for '{payload['product']}:{payload['version']}', missing 'sourcePath'."
        source_path = payload['sourcePath']
        assert source_path != "", \
            f"Cannot get source code for '{payload['product']}:{payload['version']}', empty 'sourcePath."
        assert os.path.isabs(source_path), "sourcePath: '{}' is not an absolute path!".format(source_path)
        return MavenUtils.copy_source(source_path, base_dir)

    @staticmethod
    def copy_source(source_path, base_dir):
        tmp = TemporaryDirectory(dir=base_dir)
        shutil.copytree(source_path, tmp.name, dirs_exist_ok=True)
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
    def checkout_version(base_dir, **source_config):
        repo_type = source_config['repo_type']
        repo_path = source_config['repo_path']
        version_tag = source_config['version_tag']
        assert repo_type in {"git", "svn", "hg"}, "Unknown repo type: '{}'.".format(repo_type)
        assert repo_path != "", "Empty repo_path."
        assert version_tag != "", "Empty version_tag."
        tmp = TemporaryDirectory(dir=base_dir)
        tmp_path = Path(tmp.name)
        if repo_type == "git":
            MavenUtils.git_checkout(repo_path=repo_path, version_tag=version_tag, tmp_path=tmp_path)
        elif repo_type == "svn":
            MavenUtils.svn_checkout(repo_path=repo_path, version_tag=version_tag, tmp_path=tmp_path)
        elif repo_type == "hg":
            MavenUtils.hg_checkout(repo_path=repo_path, version_tag=version_tag, tmp_path=tmp_path)
        return tmp

    @staticmethod
    def git_checkout(**source_config):
        repo_path = source_config['repo_path']
        version_tag = source_config['version_tag']
        tmp_path = source_config['tmp_path']
        repo = Repo(repo_path)
        # assert repo.tag(version_tag) is None, "Tag: '{}' does not exist.".format(version_tag)
        archive_name = version_tag+".zip"
        archive_file_name = tmp_path/archive_name
        repo.git.archive(version_tag, o=archive_file_name)
        with ZipFile(archive_file_name, 'r') as zipObj:
            zipObj.extractall(tmp_path)

    @staticmethod
    def svn_checkout(**source_config):
        raise NotImplementedError("Svn repo not supported.")
        # 'svn export' does not support tag
        # r = LocalClient(repo_path)
        # r.export(tmp_path, version_tag)

    @staticmethod
    def hg_checkout(**source_config):
        repo_path = source_config['repo_path']
        version_tag = source_config['version_tag']
        tmp_path = source_config['tmp_path']
        wd = os.getcwd()
        os.chdir(repo_path)
        cmd = [
            'hg',
            'archive',
            '-r', version_tag,
            '-t', 'files',
            tmp_path
        ]
        try:
            proc_hg = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
            out, err = proc_hg.communicate()
        except Exception as e:
            raise e
        else:
            if proc_hg.returncode:
                err_str = f"Cannot check out '{version_tag}' from repo '{repo_path}', [Error]" + str(err)
                raise Exception(err_str)
        finally:
            os.chdir(wd)


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
            "functions": {},
            "dependencyData" : {},
            "dependencyManagement" : {}
        }
        for key in tailor.keys():
            if key in payload:
                payload[key] = tailor[key]
        return payload

    @staticmethod
    def extract_from_sync(payload):
        """
        Extract content of RepoCloner in the synchronized topic.
        :param payload: payload of fasten.SyncJava.out, see
                        https://github.com/fasten-project/synchronize-javacg
        :return: payload of RepoCloner, see
                        https://github.com/fasten-project/fasten/wiki/Kafka-Topics#fastenrepocloner
        """
        extract = payload['fasten.RepoCloner.out'] if 'fasten.RepoCloner.out' in payload else payload
        return extract

    @staticmethod
    def extract_payload_from_metadata_db_ext_topic(received):
        """
        Extract content of MetaDataDB{Java|C|Python}Extension.out topic.
        :param payload: payload of MetaDataDB{Java|C|Python}Extension.out, see
                        https://github.com/fasten-project/fasten/wiki/Kafka-Topics#fastenmetadatadbextension
        :return: extracted payload
        """
        try: # MetaDataDBJavaExtension.out
            received['input']['input']['payload']['forge']
            return received['input']['input']['payload']
        except KeyError: pass
        try: # MetaDataDB{Python|C}Extension.out
            received['input']['payload']['forge']
            return received['input']['payload']
        except KeyError: pass
        try:
            received['payload']['forge']
            return received['payload']
        except KeyError: pass
        return received

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
