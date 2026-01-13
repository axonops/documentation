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

# (optional) install axon-dash dependency to enable pdf generation
install_dependency axon-dash-pdf2-predependencies
install_dependency axon-dash-pdf2

# install axon-dash
install_dependency axon-dash

# install axon-server
install_dependency axon-server