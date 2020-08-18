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
python3 entrypoint.py fasten.RepoCloner.out fasten.RapidPlugin.out fasten.RapidPlugin.err fasten.RapidPlugin.log localhost:9092 mygroup

# see if topic produced sucessfully
kafkacat -C -b localhost -t fasten.RapidPlugin.log -p 0 -o 0 -e
```

## Example json message in the produced topic
```
{
  "plugin_name": "RapidPlugin",
  "plugin_version": "0.0.1",
  "input": {
    "groupId": "fasten-project",
    "artifactId": "fasten",
    "version": "1.0.0",
    "repoPath": "/repos/fasten-project/fasten"
  },
  "created_at": "1595434993.938192",
  "payload": {
    "product": "fasten-project:fasten",
    "forge": "mvn",
    "generator": "Lizard",
    "metrics": {
      "nloc": 11188,
      "method_count": 1115,
      "complexity": -1,
      "file_list": [
        {
            "filename": "fileName.java",
            "nloc": 108,
            "function_list": [
                {
                    "name": "functionName",
                    "nloc": 8
                }
            ]
        }
      ]
    }
  }
}
```
