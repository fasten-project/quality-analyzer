# Copyright 2020 Software Improvement Group
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import shutil
import pytest
from git import Repo
from rapidplugin.utils.utils import MavenUtils, KafkaUtils

DOWNLOAD_URL_DATA = [
    ("https://repo1.maven.org/maven2/ai/api/libai/1.6.12/libai-1.6.12-sources.jar")
]

REPO_PATH_DATA = [
    ("maven/git/m1", "git", "1.0.0")
    # ("maven/svn/m2", "svn", "1.0.0"),
    # ("maven/hg/m3", "hg", "1.0.0")
]

@pytest.fixture(scope='session')
def sources_dir(tmp_path_factory):
    yield tmp_path_factory.mktemp("sources")

@pytest.fixture(scope='session')
def repos(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("repos")
    shutil.copytree('rapidplugin/tests/resources', tmp, dirs_exist_ok=True)
    yield tmp

@pytest.mark.parametrize('url', DOWNLOAD_URL_DATA)
def test_download_jar(url, sources_dir):
    source_path = MavenUtils.download_jar(url, sources_dir)
    assert str(source_path) == os.path.join(sources_dir, 'tmp')

@pytest.mark.parametrize('repo_path,repo_type,commit_tag', REPO_PATH_DATA)
def test_checkout_version(repo_path, repo_type, commit_tag, sources_dir, repos):
    repo_path = os.path.join(repos, repo_path)
    repo = Repo.init(repo_path)
    repo.git.add(".")
    repo.git.commit(m="first commit.")
    repo.create_tag('1.0.0')
    source_path = MavenUtils.checkout_version(repo_path, repo_type, commit_tag, sources_dir)
    assert str(source_path) == os.path.join(sources_dir, 'tmp')

PAYLOAD_TAILOR_DATA = [
    ({"product": "a"}, {"product": "a"}),
    ({"product": "a", "graph": {"g": ""}}, {"product": "a", "graph": {}}),
    ({"product": "a", "cha": {"c": ""}}, {"product": "a", "cha": {}}),
    ({"product": "a", "modules": {"m": ""}}, {"product": "a", "modules": {}})
]
@pytest.mark.parametrize('in_payload, out_payload', PAYLOAD_TAILOR_DATA)
def test_tailor_input(in_payload, out_payload):
    tailored = KafkaUtils.tailor_input(in_payload)
    assert tailored == out_payload

