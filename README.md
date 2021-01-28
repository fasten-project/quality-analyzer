<p align="center">
    <img src="https://user-images.githubusercontent.com/45048351/89231067-3ddbc580-d5ed-11ea-9639-2838059dda2c.jpg">
</p>
<br/>

[![BCH compliance](https://bettercodehub.com/edge/badge/fasten-project/quality-analyzer?branch=master)](https://bettercodehub.com/)
![Python Package](https://github.com/fasten-project/quality-analyzer/workflows/Python%20Package/badge.svg)

# RAPID

RAPID is the quality analysis application that SIG developes for the FASTEN project in WP3.

# Components

## RapidPlugin

RapidPlugin is a FASTEN plugin that 
generates code complexity data for the `product`.

The plugin consumes messages in the Kafka topics, 
generates code complexity data using `Lizard`, and 
produces Kafka topics with complexity data at the `callable` level.

### Input Kafka topics

The plugin will trigger different pipelines based on the `forge`, 
so the field `forge` is a mandatory in any incoming messages.
The currently supported forges are "mvn", "debian", and "PyPI". 
The plugin will raise an exception if the `forge` in the message is not supported or empty.

#### Maven
The default topic to consume: `fasten.SyncJava.out`

An example message produced by the SyncJava plugin, which merges out messages from RepoCloner and JavaCGOpal:

```json
{
  "input": {},
  "host": "fasten-repo-cloner-56dcf76495-bn4c2",
  "created_at": 1602739158,
  "plugin_name": "SyncJava",
  "fasten.RepoCloner.out" : {
    "payload": {
        "repoUrl": "",
        "date": 1291905586,
        "forge": "mvn",
        "groupId": "fasten-project",
        "artifactId": "fasten",
        "version": "1.0.0",
        "sourcesUrl": "http://fasten-project/fasten/fasten-1.0.0-sources.jar",
        "repoPath": "/mnt/fasten/repos/f/fasten-project/fasten",
        "repoType": "git",
        "commitTag": "v1.0.0"
    }
  }
}
```
The message should have all the information to identify a unique `product`.
For **Maven**, the fields `groupId`, `artifactId`, and `version` 
should not be empty. 
Missing any of these fields will cause exceptions in message consuming.

The message should have at least one way to point out the link to the source code.
- `sourcesUrl`

This field is the most reliable pointer to the versioned source code of a `product`. 

If `sourcesUrl` presents and is non-empty, the plugin will download the source code from the url specified in `sourcesUrl`.

If `sourcesUrl` does not present or is empty, the plugin will try the other sources to get the source code.

- `repoPath`

If `repoPath` is not empty, the repository of the `product` has been cloned to the FASTEN server. 
The plugin will try to check out the right version of the source code if both `repoType` and `commitTag` are non-empty.
The currently supported`repoType` are "git", "svn", and "hg". 
The plugin will raise an exception if the `repoType` in the message is not supported.

If none of the above efforts succeed, the plugin will raise an exception 
specifying that it cannot get the source code.

#### PyPI
The current topic to consume: `fasten.pycg.with_sources.out`

An example message:

```json
{
  "input": {},
  "plugin_name": "PyCG",
  "plugin_version": "0.0.1",
  "created_at": "1596576724",
  "payload": {
    "product": "gud",
    "forge": "PyPI",
    "generator": "PyCG",
    "depset": [],
    "version": "1.0.10",
    "timestamp": "1561421985",
    "modules": {
    },
    "graph":{},
    "cha": {},
    "metadata": {},
    "sourcePath": "/mnt/fasten/pypi-test/final/sources/g/gud/1.0.10"
  }
}
```

The message should have all the information to identify a unique `product`.
For **PyPI**, the fields `product`, and `version` should not be empty. 
Missing any of these fields will cause exceptions in message consuming.

If `sourcePath` is empty, the plugin will raise an exception.

#### Debian 
The current topic to consume: `fasten.debian.cg.2`

An example message:

```json
{
  "plugin_name": "CScoutKafkaPlugin",
  "plugin_version": "0.0.1",
  "input": {
    "package": "sed",
    "version": "4.7-1",
    "arch": "amd64",
    "release": "buster",
    "source": "sed",
    "source_version": "4.7-1",
    "date": ""
  },
  "created_at": "1600861444.064117",
  "payload": {
    "forge": "debian",
    "release": "",
    "product": "sed",
    "version": "4.7-1",
    "source": "sed",
    "architecture": "amd64",
    "generator": "cscout",
    "timestamp": "1545470644",
    "depset": [],
    "build_depset": [],
    "undeclared_depset": [],
    "graph": {},
    "functions": {},
    "profiling_data": {},
    "sourcePath": "/mnt/fasten/debian/sources/s/sed/4.7-1"
  }
}
```
Similar to **PyPI**, the fields `product`, and `version` should not be empty. 
Missing any of these fields will cause exceptions in message consuming.

If `sourcePath` is empty, the plugin will raise an exception.

### Output Kafka topics

The field `input` in the output topic is used for tracking upstreaming plugins and 
usually copies the whole `payload` from the consumed message. 
To avoid potential large message in the output topics, 
the plugin will tailor the `payload` of consumed message. 
The content of the following fields will be tailored. 

**PyPI**: `fasten.pycg.with_sources.out`
- `depset`
- `cha`
- `graph`
- `modules`

**Debian**: `fasten.debian.cg.2`
- `depset`
- `build_depset`
- `undeclared_depset`
- `graph`
- `functions`

#### Output topic
The default topic to produce: `fasten.RapidPlugin.callable.out`

An example message:
```json
{
  "plugin_name": "RapidPlugin",
  "plugin_version": "0.0.1",
  "input": {},
  "created_at": "1595434993",
  "payload": {
    "quality_analyzer_name": "Lizard",
    "quality_analyzer_version": "1.17.7",
    "quality_analysis_timestamp": "1596455923",
    "product": "fasten-project:fasten",
    "version": "1.0.0",
    "forge": "mvn",
    "language": "java",
    "filename": "/fasten/core/server.java",
    "callable_name": "callable",
    "callable_long_name": "callable(int i)",
    "start_line": 33,
    "end_line": 42,
    "metrics": {
      "nloc": 10,
      "complexity": 5,
      "token_count": 20,
      "parameters": ["i"],
      "parameter_count": 1,
      "length": 10
    }
  }
}
```

#### Log topic
The default topic to produce: `fasten.RapidPlugin.callable.log`

#### Error topic
The default topic to produce: `fasten.RapidPlugin.callable.err`
