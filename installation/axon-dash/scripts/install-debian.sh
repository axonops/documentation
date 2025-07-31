sudo apt-get update
sudo apt-get install -y curl gnupg ca-certificates

curl -L https://packages.axonops.com/apt/repo-signing-key.gpg \
  | sudo gpg --dearmor -o /usr/share/keyrings/axonops.gpg

echo "deb [arch=arm64,amd64 signed-by=/usr/share/keyrings/axonops.gpg]\
  https://packages.axonops.com/apt axonops-apt main" \
  | sudo tee /etc/apt/sources.list.d/axonops-apt.list
sudo apt-get update

sudo apt-get install -y axon-dash