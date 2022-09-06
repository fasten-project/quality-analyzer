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

########################################################################################
FROM python:3.10-slim-bullseye
########################################################################################
LABEL maintainer="Software Improvement Group Research <research@sig.eu>"

USER root

RUN apt-get update \
 && apt-get install -y -qq \
        libsnappy-dev

WORKDIR /plugin

COPY rapidplugin rapidplugin/
COPY integration_tests/*.py integration_tests/
COPY entrypoint.py .
COPY setup.py .
COPY requirements.txt .
COPY README.md .

RUN python -m pip install -r requirements.txt

ENTRYPOINT ["python", "/plugin/entrypoint.py"]
