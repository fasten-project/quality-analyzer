#  Prerequisites

```
docker
docker-compose
```

# Setup

To setup a Kafka cluster, execute the following in ```kafka-docker/```

``` console
docker-compose -f docker-compose-single-broker.yml up -d
```

The Kafka cluster will exist on the Docker network ```kafka-docker_default```, where the broker will be reachable at ```kafka:29092```.

From outside the Docker network, the broker is reachable at ```localhost:9092```.

# Testing

To test putting data into a topic, run the following:
``` console
docker run -i --rm --network=kafka-docker_default \
    edenhill/kafkacat:1.6.0 kafkacat \
    -b kafka:29092 -t fasten.RepoCloner.out -P \
    < rapidplugin/integration_tests/resources/fasten.RepoCloner.out-testdata.txt
```

Run the following to verify that the data was inserted:
``` console
docker run -it --rm --network=kafka-docker_default \
    edenhill/kafkacat:1.6.0 kafkacat \
    -b kafka:29092 -t fasten.RepoCloner.out -C
```
