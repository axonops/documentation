# define installation helper function
function install_dependency() {
  service=${1}

  mkdir -p "/var/cache/apt/archives/${service}"
  tar xf "${service}.deb.tgz" --directory "/var/cache/apt/archives/${service}"
  while ! sudo dpkg -i /var/cache/apt/archives/${service}/*.deb; do
    echo "Working through dependencies..."
  done
}

# install axon-dash
install_dependency axon-dash-pdf-predependencies
install_dependency axon-dash-pdf
install_dependency axon-dash

# install axon-server
install_dependency axon-dash

# install axon-agent on Cassandra node
install_dependency axon-agent

# install matching axon-cassandra agent on Cassandra node (choose one)
install_dependency axon-cassandra3.0-agent
install_dependency axon-cassandra3.11-agent
install_dependency axon-cassandra4.0-agent
install_dependency axon-cassandra4.0-agent-jdk8
install_dependency axon-cassandra4.1-agent
install_dependency axon-cassandra4.1-agent-jdk8
install_dependency axon-cassandra5.0-agent-jdk11
install_dependency axon-cassandra5.0-agent-jdk17