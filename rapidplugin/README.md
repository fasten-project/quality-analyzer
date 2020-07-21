# Rapid plugin

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
kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic fasten.RapidPlugin.error
kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic fasten.RapidPlugin.log

# add message to topic for consuming
echo '{"groupId":"fasten-project", artifactId": "fasten", "version": "1.0.0", "repoPath": "https://github.com/fasten-project/fasten.git"}' | \
    kafka-console-producer.sh --broker-list localhost:9092 --topic fasten.RepoCloner.out

# see if topic added sucessfully
kafkacat -C -b localhost -t fasten.RepoCloner.out -p 0 -o 0 -e

# run plugin
python3 entrypoint.py fasten.RepoCloner.out fasten.RapidPlugin.out fasten.RapidPlugin.err fasten.RapidPlugin.log localhost:9092 mygroup 1

# see if topic produced sucessfully
kafkacat -C -b localhost -t fasten.RapidPlugin.log -p 0 -o 0 -e
```