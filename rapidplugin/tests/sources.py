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
