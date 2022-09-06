<p align="center">
    <img src="https://user-images.githubusercontent.com/45048351/89231067-3ddbc580-d5ed-11ea-9639-2838059dda2c.jpg">
</p>
<br/>

[![BCH compliance](https://bettercodehub.com/edge/badge/fasten-project/quality-analyzer?branch=master)](https://bettercodehub.com/)
![Python Package](https://github.com/fasten-project/quality-analyzer/workflows/Python%20Package/badge.svg)

# RAPID Quality Analzer

RAPID is the quality analysis application that SIG developes for the FASTEN project in WP3.

The RAPID Quality Analyzer is a FASTEN server plugin that produces
code quality metrics for a given code base. The code bases are assumed
to be downloaded previously. The plugin consumes from a Kafka input topic to 
start processing a code base.

## Input topic

Default: `fasten.SourcesProvider.out`
```json
{
    "forge": "mvn",
    "product": "m1",
    "version": "1.0.0",
    "sourcePath": "maven/m1"
}

{
    "forge": "debian",
    "product": "d1",
    "version": "1.0.0",
    "sourcePath": "debian/d1"
}

{
    "forge": "PyPI",
    "product": "p1",
    "version": "1.0.0",
    "sourcePath": "pypi/p1"
}
```

## Output topics

Messages are produced to various topics, which can be configured through command line options.

Progress messages (`--produce_topic`): `fasten.RapidPlugin.out`.
Error messages (`--error_topic`): `fasten.RapidPlugin.err`.
Detailed log messages (`--log_topic`): `fasten.RapidPlugin.log`.

Callables with code quality metadata (`--produce_callable_topic`): `fasten.RapidPlugin.callable.out`.

Callable messages have the following JSON format:
```json
{
  "plugin_name": "RapidPlugin",
  "plugin_version": "1.3.0",
  "input": {
    "forge": "mvn",
    "product": "log4j:log4j",
    "version": "1.2.15",
    "sourcePath": "/mnt/fasten/sources/mvn/l/log4j/log4j/1.2.15"
  },
  "created_at": "1662453047.404707",
  "payload": {
    "product": "log4j:log4j",
    "version": "1.2.15",
    "forge": "mvn",
    "language": "java",
    "quality_analyzer_name": "Lizard",
    "quality_analyzer_version": "1.17.10",
    "quality_analysis_timestamp": "1662453043.327921",
    "filename": "org/apache/log4j/chainsaw/ControlPanel.java",
    "callable_name": "ControlPanel::ControlPanel",
    "callable_long_name": "ControlPanel::ControlPanel( final MyTableModel aModel)",
    "callable_parameters": [
      "aModel"
    ],
    "start_line": 50,
    "end_line": 221,
    "metrics": {
      "nloc": 146,
      "complexity": 2,
      "token_count": 1002,
      "length": 172,
      "parameter_count": 1
    }
  }
}
```
