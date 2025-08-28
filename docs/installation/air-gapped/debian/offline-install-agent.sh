#!/usr/bin/env /bin/bash

# define installation helper function
function install_dependency() {
  service=${1}

  mkdir -p "/opt/offline/axonops/${service}"
  tar xf "${service}.deb.tgz" --directory "/opt/offline/axonops/${service}"
  if [[ "$service" == "axon-dash-pdf2-predependencies" ]]; then
    sudo dpkg -i /opt/offline/axonops/${service}/libpython3*-minimal*
    sudo dpkg -i /opt/offline/axonops/${service}/python3*-minimal*
    sudo dpkg -i /opt/offline/axonops/${service}/*.deb || (
      echo "Working through Python dependencies..."
      sudo dpkg -i /opt/offline/axonops/${service}/*.deb
    )
  else
    sudo dpkg -i /opt/offline/axonops/${service}/*.deb
  fi
}

# install axon-agent on Cassandra/Kafka nodes
install_dependency axon-agent

## (choose one of the following)
## install matching axon-cassandra/axon-kafka agent on the Cassandra/Kafka nodes
# install_dependency axon-cassandra3.0-agent
# install_dependency axon-cassandra3.11-agent
# install_dependency axon-cassandra4.0-agent
# install_dependency axon-cassandra4.0-agent-jdk8
# install_dependency axon-cassandra4.1-agent
# install_dependency axon-cassandra4.1-agent-jdk8
# install_dependency axon-cassandra5.0-agent-jdk11
# install_dependency axon-cassandra5.0-agent-jdk17
# install_dependency axon-kafka2-agent
# install_dependency axon-kafka3-agent