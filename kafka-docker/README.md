# Installation

## Prerequisites

```
docker  
docker-compose
```

## Setup

To setup a Kafka cluster, execute the following in ```kafka-docker/```

```
$ docker-compose -f docker-compose-single-broker.yml up -d
```

The Kafka cluster will exist on the Docker network ```kafka-docker_default```, where the broker will be reachable at ```kafka:29092```.

From outside the Docker network, the broker is reachable at ```localhost:9202```.

## Testing

To test putting data into a topic, try the following after first cloning ```https://github.com/fasten-project/fasten``` into the parent directory containing RAPID.

    $ docker run --interactive --rm --network=kafka-docker_default \  
        edenhill/kafkacat:1.6.0 kafkacat \  
        -b kafka:29092 -t maven.packages \  
        -K: -P < ../fasten/dataset/mvn.dataset.txt

