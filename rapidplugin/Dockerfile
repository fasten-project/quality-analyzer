FROM openjdk:11.0-buster

USER root

RUN apt-get update \
 && apt-get install -y -qq \
        python3 \
        curl \
        kafkacat

RUN useradd kafka -m

USER kafka

WORKDIR /home/kafka

COPY start_kafka.sh /home/kafka/start_kafka.sh

RUN curl "https://archive.apache.org/dist/kafka/2.1.1/kafka_2.11-2.1.1.tgz" -o kafka.tgz \
 && tar -xvzf kafka.tgz --strip 1

USER root

CMD ["./start_kafka.sh"]

# ENTRYPOINT ["/bin/bash"]
