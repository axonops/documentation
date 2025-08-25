# define installation helper function
function install_dependency() {
  service=${1}

  mkdir -p "/var/cache/apt/archives/${service}"
  tar xf "${service}.deb.tgz" --directory "/var/cache/apt/archives/${service}"
  if [[ "$service" == "axon-dash-pdf-predependencies" ]]; then
    sudo dpkg -i /var/cache/apt/archives/${service}/libpython3.9-minimal*
    sudo dpkg -i /var/cache/apt/archives/${service}/python3.9-minimal*
    sudo dpkg -i /var/cache/apt/archives/${service}/*.deb || (
      echo "Working through Python dependencies..."
      sudo dpkg -i /var/cache/apt/archives/${service}/*.deb
    )
  else
    sudo dpkg -i /var/cache/apt/archives/${service}/*.deb
  fi
}

# install axon-dash
install_dependency axon-dash-pdf-predependencies
install_dependency axon-dash-pdf
install_dependency axon-dash

# install axon-server
install_dependency axon-server

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