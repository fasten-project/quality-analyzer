# Rapid plugin

## Test and debug

```
# start server
bin/zookeeper-server-start.sh config/zookeeper.properties &
bin/kafka-server-start.sh config/server.properties &

# creat topic
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic fasten.RepoCloner.out
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic fasten.RapidPlugin.out
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic fasten.RapidPlugin.error
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic fasten.RapidPlugin.log

# add message to topic for consuming
echo '{"artifactID": "fasten", "version": "1.0.0", "repoPath": "https://github.com/fasten-project/fasten.git"}' | \
    bin/kafka-console-producer.sh --broker-list localhost:9092 --topic fasten.RepoCloner.out

# see if topic added sucessfully
kafkacat -C -b localhost -t fasten.RepoCloner.out -p 0 -o 0 -e

# run plugin
python3 entrypoint.py fasten.RepoCloner.out fasten.RapidPlugin.out fasten.RapidPlugin.err fasten.RapidPlugin.log localhost:9092 mygroup 1

# see if topic produced sucessfully
kafkacat -C -b localhost -t fasten.RapidPlugin.log -p 0 -o 0 -e
```