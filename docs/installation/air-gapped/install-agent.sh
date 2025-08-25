# ensure the axon-agent is not running
systemctl stop axon-agent

# configure the agent
vi /etc/axonops/axon-agent.yml

# configure Cassandra to load the agent
vi /etc/cassandra/cassandra-env.sh

# restart the agent
systemctl restart axon-agent

# restart Cassandra to load the agent
systemctl restart cassandra