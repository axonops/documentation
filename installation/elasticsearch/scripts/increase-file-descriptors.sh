sudo mkdir -p /etc/security/limits.conf.d
echo 'elasticsearch  -  nofile  65536' \
    | sudo tee --append /etc/security/limits.conf.d/elastic.conf