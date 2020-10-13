# Rapid plugin

## Installation

Run the following either normally or in a virtual environment:
``` console
pip install -r requirements.txt
```

## Test and debug

```
# install Kafka and kafkacat
Go to '{path_to_kafka}/bin', or add '{path_to_kafka}/bin' to system path.

# start server
zookeeper-server-start.sh config/zookeeper.properties &
kafka-server-start.sh config/server.properties &

# creat topic
kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic fasten.RepoCloner.out
kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic fasten.RapidPlugin.out
kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic fasten.RapidPlugin.err
kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic fasten.RapidPlugin.log

# add message to topic for consuming
echo '{"groupId": "fasten-project", "artifactId": "fasten", "version": "1.0.0", "repoPath": "~/repos/fasten"}' | \
    kafka-console-producer.sh --broker-list localhost:9092 --topic fasten.RepoCloner.out

# see if topic added sucessfully
kafkacat -C -b localhost -t fasten.RepoCloner.out -p 0 -o 0 -e

# run plugin
python3 entrypoint.py fasten.RepoCloner.out fasten.RapidPlugin.out fasten.RapidPlugin.err fasten.RapidPlugin.log localhost:9092 mygroup 1

# see if topic produced sucessfully
kafkacat -C -b localhost -t fasten.RapidPlugin.log -p 0 -o 0 -e
```

## Kafka message format for the topic fasten.RapidPlugin.callables.out
```
{
  "plugin_name": "RapidPlugin",
  "plugin_version": "0.0.1",
  "input": {
    ...
  },
  "created_at": "1595434993.938192",
  "payload": {
    "analyzer_name": "Lizard",
    "analyzer_version": "1.17.5",
    "analysis_timestamp": "datetime of Lizard run",
    "product": "fasten-project:fasten",
    "version": "1.0.0"
    "forge": "mvn",
    "language": "java"
    "filepath": "/fasten/core/server.java",
    "name": "callable",
    "long_name": "callable(int i)",
    "start_line": 33,
    "end_line": 42,
    "metrics": {
      "nloc": 11188,
      "complexity": 10,
      ...
    }
  }
}
```
