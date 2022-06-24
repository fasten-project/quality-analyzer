# Copyright 2022 Software Improvement Group
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
from pathlib import Path
from rapidplugin.utils import Utils


@pytest.mark.parametrize('old, prefix, new', [
    ('/abs_path/rel_dir/d1.c', '/abs_path', 'rel_dir/d1.c')
])
def test_relativize_filename(old, prefix, new):
    new_file_name = Utils.relativize_filename(old, prefix)
    assert Path(new_file_name) == Path(new)
