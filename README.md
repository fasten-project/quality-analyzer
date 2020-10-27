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

#### Maven
`fasten.RepoCloner.out`

An example message:

```json
{
  "input": {
     ...
  },
  "host": "fasten-repo-cloner-56dcf76495-bn4c2",
  "created_at": 1602739158,
  "plugin_name": "RepoCloner",
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
```
The message should have all the information to identify a unique `product`.
For `Maven`, the fields `forge`, `groupId`, `artifactId`, and `version` 
should not be empty. 
Missing any of these fields will cause exceptions in message consuming.

The message should have at least one way to point out the source to the code.
If `sourcesUrl` presents and is non-empty, the plugin will download the source code.



#### PyPI

#### Debian 

### Output Kafka topics

#### Output topic

#### Log topic

#### Error topic
