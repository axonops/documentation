CASSANDRA_GROUP=cassandra
CASSANDRA_USER=cassandra

sudo usermod -aG "$CASSANDRA_GROUP" axonops
sudo usermod -aG axonops "$CASSANDRA_USER"