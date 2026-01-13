#!/usr/bin/env /bin/bash

# extract packages into the offline repository location
sudo mkdir -p /opt/offline/axonops
sudo tar -C /opt/offline/axonops \
  -xzf ./axonops-x86_64.rpm.tgz \
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

  sudo dnf5 \
    --disablerepo='*' \
    --enablerepo="axonops-offline" \
    install \
    -y \
    --nogpgcheck \
    "${service}"
}

# (optional) install axon-dash dependency to enable pdf generation
install_dependency axon-dash-pdf2
install_dependency axon-dash

# install axon-server
install_dependency axon-server