# configure axon-server
systemctl stop axon-server
vi /etc/axonops/axon-server.yml
systemctl restart axon-server

# configure axon-dash
systemctl stop axon-dash
vi /etc/axonops/axon-dash.yml
systemctl restart axon-dash
