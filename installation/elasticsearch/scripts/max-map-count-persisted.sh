echo "vm.max_map_count = 262144" \
    | sudo tee --append /etc/sysctl.d/10-elasticsearch.conf