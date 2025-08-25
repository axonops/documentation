# install dependency needed for creating repomd repository
sudo dnf install -y createrepo_c

# setup AxonOps repository
cat >/etc/yum.repos.d/axonops-yum.repo <<EOF
[axonops-yum]
name=axonops-yum
baseurl=https://packages.axonops.com/yum/
enabled=1
repo_gpgcheck=0
gpgcheck=0
EOF