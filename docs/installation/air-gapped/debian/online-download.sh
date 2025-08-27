#!/usr/bin/env /bin/bash

# download axonops packages and dependencies
services=(
  axon-dash-pdf2
  axon-dash
  axon-server
  axon-agent
  axon-cassandra3.0-agent
  axon-cassandra3.11-agent
  axon-cassandra4.0-agent
  axon-cassandra4.0-agent-jdk8
  axon-cassandra4.1-agent
  axon-cassandra4.1-agent-jdk8
  axon-cassandra5.0-agent-jdk11
  axon-cassandra5.0-agent-jdk17
)
for service in "${services[@]}"; do
  # create temporary location for downloading packages
  mkdir -p "/tmp/downloads/${service}"
  cd "/tmp/downloads/${service}"

  # download dependencies
  sudo apt-get download $(\
    sudo apt-rdepends "${service}" \
      | grep -v "^ " \
      | sed 's|debconf-2.0|debconf|' \
      | sed 's|libappindicator1|libayatana-appindicator3-1|' \
      | sed 's|libgcc1|libgcc-s1|' \
      | sed 's|default-dbus-session-bus|dbus-user-session|' \
      | sed 's|dbus-session-bus|dbus|' \
      | sed 's|^gsettings-backend$||' \
    )
  # create Packages index files
  dpkg-scanpackages $(pwd) /dev/null | gzip -9c > Packages.gz

  # create tarball with downloaded packages
  mkdir -p "/tmp/bundles"
  tar -czf "/tmp/bundles/${service}.deb.tgz" .
done