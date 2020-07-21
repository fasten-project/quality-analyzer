#!/bin/bash

set -m

/home/kafka/bin/zookeeper-server-start.sh /home/kafka/config/zookeeper.properties &
/home/kafka/bin/kafka-server-start.sh /home/kafka/config/server.properties &

fg %1
