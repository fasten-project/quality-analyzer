########################################################################################
FROM python:3.9-slim-buster
########################################################################################
LABEL maintainer="Software Improvement Group Research <research@sig.eu>"

USER root

RUN apt-get update \
 && apt-get install -y -qq \
        git \
        subversion \
        mercurial

RUN git config --global user.email "research@softwareimprovementgroup.com" \
 && git config --global user.name "Software Improvement Group Research"

WORKDIR /plugin

COPY rapidplugin rapidplugin/
COPY entrypoint.py .
COPY setup.py .
COPY requirements.txt .
COPY README.md .

RUN python -m pip install -r requirements.txt

ENTRYPOINT ["python", "/home/plugin/entrypoint.py"]
