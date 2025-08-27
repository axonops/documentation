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

# (optional) install axon-dash dependency to enable pdf generation
install_dependency axon-dash-pdf2-predependencies
install_dependency axon-dash-pdf2

# install axon-dash
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