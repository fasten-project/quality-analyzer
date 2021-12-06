# Copyright 2021 Software Improvement Group
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


@pytest.fixture(scope='session')
def sources(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("sources")
    shutil.copytree('rapidplugin/tests/resources', tmp, dirs_exist_ok=True)
    yield tmp

    
def fix_sourcePath(record, tmp_sources_path):
    if "sourcePath" in record:
        sourcePath = record["sourcePath"]
        record.update({"sourcePath": os.path.join(tmp_sources_path, sourcePath)})
    return record
