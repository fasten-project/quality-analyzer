########################################################################################
FROM python:3.8-slim-buster
########################################################################################
LABEL maintainer="Software Improvement Group Research <research@sig.eu>"

USER root

RUN apt-get update \
 && apt-get install -y -qq \
        git \
        subversion \
        mercurial

RUN useradd -m plugin

USER plugin

WORKDIR /home/plugin

COPY --chown=plugin rapidplugin rapidplugin/
COPY --chown=plugin entrypoint.py .
COPY --chown=plugin setup.py .
COPY --chown=plugin requirements.txt .
COPY --chown=plugin README.md .

RUN python -m pip install -r requirements.txt

ENTRYPOINT ["python", "/home/plugin/entrypoint.py"]
