#!/usr/bin/env /bin/bash

# create temporary location for downloading packages
mkdir -p "/tmp/downloads/axon-dash-pdf2-predependencies"
cd "/tmp/downloads/axon-dash-pdf2-predependencies"

# install predependencies for axon-dash-pdf2
services=(
  dbus-user-session
  libayatana-appindicator1
  libayatana-appindicator3-1
  libdbusmenu-glib4
  libayatana-indicator3-7
  libdbusmenu-gtk3-4
  python3
  libappindicator1
)
for service in "${services[@]}"; do
  # download axon-dash-pdf2 virtual package predependencies
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
done

# create Packages index files
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz

# create tarball with downloaded packages
mkdir -p "/tmp/bundles"
tar -czf "/tmp/bundles/axon-dash-pdf2-predependencies.deb.tgz" .