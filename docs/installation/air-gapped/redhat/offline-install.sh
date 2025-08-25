# extract packages into the offline repository location
sudo mkdir -p /opt/offline/axonops
sudo tar -C /opt/offline/axonops \
  -xzf ./axonops_repo_x86_64.rpm.tgz \
  --strip-components=1

# setup the offline repository
sudo tee /etc/yum.repos.d/axonops-offline.repo \
  >/dev/null <<'EOF'
[axonops-offline]
name=AxonOps Offline
baseurl=file:///opt/offline/axonops
enabled=1
gpgcheck=0
EOF

# define installation helper function
function install_dependency() {
  service=${1}

  sudo dnf5 clean all
  sudo dnf5 makecache
  sudo dnf5 \
    --disablerepo='*' \
    --enablerepo="axonops-offline" \
    install \
    -y \
    --nogpgcheck \
    "${service}"
}

# install axon-dash
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