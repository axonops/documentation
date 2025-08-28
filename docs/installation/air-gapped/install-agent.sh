# ensure the axon-agent is not running
systemctl stop axon-agent

# configure the agent
vi /etc/axonops/axon-agent.yml

## FOR CASSANDRA

# configure Cassandra to load the agent
vi /etc/cassandra/cassandra-env.sh

# configure Cassandra user groups
sudo usermod -aG "$CASSANDRA_GROUP" axonops
sudo usermod -aG axonops "$CASSANDRA_USER"

# restart Cassandra to load the agent
systemctl restart cassandra

## FOR KAFKA

# configure Kafka to load the agent
vi "$KAFKA_HOME/bin/kafka-server-start.sh"

# configure Kafka user groups
sudo usermod -aG "$KAFKA_GROUP" axonops
sudo usermod -aG axonops "$KAFKA_USER"

# restart Kafka to load the agent
vi "$KAFKA_HOME/bin/kafka-server-stop.sh"
vi "$KAFKA_HOME/bin/kafka-server-start.sh"

## FOR BOTH

# restart the agent
systemctl restart axon-agent