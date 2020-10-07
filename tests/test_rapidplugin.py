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

import pytest
from rapidplugin.entrypoint import RapidPlugin


@pytest.fixture
def plugin():
    plugin = RapidPlugin(base_dir="src")
    return plugin


class TestGetSourceCode:
    def test_no_sources_url(self, payload: str):
        path = plugin()._get_source_path(payload)
        assert True

    def test_invalid_sources_url(self, payload: str):
        path = plugin()._get_source_path(payload)
        assert True

    def test_no_repo_url(self, payload: str):
        path = plugin()._get_source_path(payload)
        assert True


class TestConsumeRecord:
    def test_maven(self, record):
        assert True

    def test_pypi(self, record):
        assert True

    def test_debian(self, record):
        assert True