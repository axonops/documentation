# Certificate Types and Generation

This section covers the types of certificates used in Cassandra deployments and provides procedures for generating them.

## Certificate Types

### Server Certificates

Server certificates identify Cassandra nodes to clients and other nodes. Each node requires its own certificate with a unique identity.

**Requirements:**
- Subject or SAN must match the node's hostname or IP address
- Extended Key Usage: `serverAuth`
- Key Usage: `digitalSignature`, `keyEncipherment`

### Client Certificates

Client certificates identify applications connecting to Cassandra. Required when mutual TLS (mTLS) is enabled.

**Requirements:**
- Subject identifies the client application or user
- Extended Key Usage: `clientAuth`
- Key Usage: `digitalSignature`

### CA Certificates

Certificate Authority certificates sign server and client certificates. CA certificates are placed in truststores.

**Types:**
- Root CA: Self-signed, trust anchor
- Intermediate CA: Signed by Root, signs end-entity certificates

---

## Certificate Generation

### Option 1: Self-Signed Certificates (Development)

Self-signed certificates are appropriate for development and testing only.

```bash
#!/bin/bash
# generate-self-signed.sh

NODE_NAME="cassandra-node-1"
VALIDITY_DAYS=365
KEY_SIZE=2048

# Generate private key and self-signed certificate
openssl req -x509 -newkey rsa:${KEY_SIZE} \
    -keyout ${NODE_NAME}-key.pem \
    -out ${NODE_NAME}-cert.pem \
    -days ${VALIDITY_DAYS} \
    -nodes \
    -subj "/CN=${NODE_NAME}"

# Create PKCS12 keystore
openssl pkcs12 -export \
    -in ${NODE_NAME}-cert.pem \
    -inkey ${NODE_NAME}-key.pem \
    -out ${NODE_NAME}-keystore.p12 \
    -name ${NODE_NAME} \
    -password pass:cassandra

# Create truststore with the certificate
keytool -import \
    -file ${NODE_NAME}-cert.pem \
    -keystore truststore.jks \
    -storepass cassandra \
    -noprompt \
    -alias ${NODE_NAME}
```

### Option 2: Private CA (Production)

A private CA provides centralized certificate management for production deployments.

#### Step 1: Create Root CA

```bash
#!/bin/bash
# create-root-ca.sh

CA_DIR="./ca"
mkdir -p ${CA_DIR}/{certs,crl,newcerts,private}
touch ${CA_DIR}/index.txt
echo 1000 > ${CA_DIR}/serial

# Generate Root CA private key
openssl genrsa -aes256 -out ${CA_DIR}/private/ca-key.pem 4096
chmod 400 ${CA_DIR}/private/ca-key.pem

# Generate Root CA certificate
openssl req -config openssl-ca.cnf \
    -key ${CA_DIR}/private/ca-key.pem \
    -new -x509 -days 3650 -sha256 \
    -extensions v3_ca \
    -out ${CA_DIR}/certs/ca-cert.pem \
    -subj "/C=US/ST=California/O=Example Corp/CN=Example Root CA"

chmod 444 ${CA_DIR}/certs/ca-cert.pem
```

#### Step 2: Create Intermediate CA (Optional but Recommended)

```bash
#!/bin/bash
# create-intermediate-ca.sh

INT_DIR="./ca/intermediate"
mkdir -p ${INT_DIR}/{certs,crl,csr,newcerts,private}
touch ${INT_DIR}/index.txt
echo 1000 > ${INT_DIR}/serial

# Generate Intermediate CA private key
openssl genrsa -aes256 -out ${INT_DIR}/private/intermediate-key.pem 4096
chmod 400 ${INT_DIR}/private/intermediate-key.pem

# Generate CSR for Intermediate CA
openssl req -config openssl-intermediate.cnf \
    -new -sha256 \
    -key ${INT_DIR}/private/intermediate-key.pem \
    -out ${INT_DIR}/csr/intermediate.csr \
    -subj "/C=US/ST=California/O=Example Corp/CN=Example Intermediate CA"

# Sign with Root CA
openssl ca -config openssl-ca.cnf \
    -extensions v3_intermediate_ca \
    -days 1825 -notext -md sha256 \
    -in ${INT_DIR}/csr/intermediate.csr \
    -out ${INT_DIR}/certs/intermediate-cert.pem

# Create certificate chain
cat ${INT_DIR}/certs/intermediate-cert.pem \
    ./ca/certs/ca-cert.pem > ${INT_DIR}/certs/ca-chain.pem
```

#### Step 3: Generate Node Certificates

```bash
#!/bin/bash
# generate-node-cert.sh

NODE_NAME=$1
if [ -z "$NODE_NAME" ]; then
    echo "Usage: $0 <node-name>"
    exit 1
fi

INT_DIR="./ca/intermediate"
CERT_DIR="./certs/${NODE_NAME}"
mkdir -p ${CERT_DIR}

# Generate node private key
openssl genrsa -out ${CERT_DIR}/${NODE_NAME}-key.pem 2048
chmod 400 ${CERT_DIR}/${NODE_NAME}-key.pem

# Create SAN configuration
cat > ${CERT_DIR}/san.cnf << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]
CN = ${NODE_NAME}

[v3_req]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${NODE_NAME}
DNS.2 = ${NODE_NAME}.example.com
DNS.3 = localhost
IP.1 = 127.0.0.1
EOF

# Generate CSR with SAN
openssl req -new \
    -key ${CERT_DIR}/${NODE_NAME}-key.pem \
    -out ${CERT_DIR}/${NODE_NAME}.csr \
    -config ${CERT_DIR}/san.cnf \
    -subj "/C=US/ST=California/O=Example Corp/CN=${NODE_NAME}"

# Sign with Intermediate CA
openssl x509 -req \
    -in ${CERT_DIR}/${NODE_NAME}.csr \
    -CA ${INT_DIR}/certs/intermediate-cert.pem \
    -CAkey ${INT_DIR}/private/intermediate-key.pem \
    -CAcreateserial \
    -out ${CERT_DIR}/${NODE_NAME}-cert.pem \
    -days 365 \
    -sha256 \
    -extensions v3_req \
    -extfile ${CERT_DIR}/san.cnf

# Create certificate chain for node
cat ${CERT_DIR}/${NODE_NAME}-cert.pem \
    ${INT_DIR}/certs/intermediate-cert.pem > ${CERT_DIR}/${NODE_NAME}-chain.pem
```

#### Step 4: Create Keystores and Truststores

```bash
#!/bin/bash
# create-stores.sh

NODE_NAME=$1
CERT_DIR="./certs/${NODE_NAME}"
STORE_PASS="cassandra"

# Create PKCS12 keystore with certificate chain
openssl pkcs12 -export \
    -in ${CERT_DIR}/${NODE_NAME}-chain.pem \
    -inkey ${CERT_DIR}/${NODE_NAME}-key.pem \
    -out ${CERT_DIR}/${NODE_NAME}-keystore.p12 \
    -name ${NODE_NAME} \
    -password pass:${STORE_PASS}

# Convert to JKS if needed
keytool -importkeystore \
    -srckeystore ${CERT_DIR}/${NODE_NAME}-keystore.p12 \
    -srcstoretype PKCS12 \
    -srcstorepass ${STORE_PASS} \
    -destkeystore ${CERT_DIR}/${NODE_NAME}-keystore.jks \
    -deststoretype JKS \
    -deststorepass ${STORE_PASS}

# Create truststore with CA chain
keytool -import \
    -file ./ca/intermediate/certs/ca-chain.pem \
    -keystore ${CERT_DIR}/truststore.jks \
    -storepass ${STORE_PASS} \
    -noprompt \
    -alias ca-chain
```

---

## OpenSSL Configuration Files

### Root CA Configuration (openssl-ca.cnf)

```ini
[ ca ]
default_ca = CA_default

[ CA_default ]
dir               = ./ca
certs             = $dir/certs
crl_dir           = $dir/crl
new_certs_dir     = $dir/newcerts
database          = $dir/index.txt
serial            = $dir/serial
private_key       = $dir/private/ca-key.pem
certificate       = $dir/certs/ca-cert.pem
crl               = $dir/crl/ca.crl.pem
crlnumber         = $dir/crlnumber
default_md        = sha256
default_days      = 375
preserve          = no
policy            = policy_loose

[ policy_loose ]
countryName             = optional
stateOrProvinceName     = optional
localityName            = optional
organizationName        = optional
organizationalUnitName  = optional
commonName              = supplied
emailAddress            = optional

[ req ]
default_bits        = 4096
distinguished_name  = req_distinguished_name
string_mask         = utf8only
default_md          = sha256

[ req_distinguished_name ]
countryName                     = Country Name
stateOrProvinceName             = State
localityName                    = Locality
organizationName                = Organization
commonName                      = Common Name

[ v3_ca ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true
keyUsage = critical, digitalSignature, cRLSign, keyCertSign

[ v3_intermediate_ca ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true, pathlen:0
keyUsage = critical, digitalSignature, cRLSign, keyCertSign
```

---

## Certificate Verification

### Verify Certificate Chain

```bash
# Verify server certificate against CA chain
openssl verify -CAfile ca-chain.pem server-cert.pem

# Verify with verbose output
openssl verify -CAfile ca-chain.pem -verbose server-cert.pem
```

### Verify Certificate Details

```bash
# View certificate contents
openssl x509 -in server-cert.pem -noout -text

# Check expiration
openssl x509 -in server-cert.pem -noout -dates

# Check subject and issuer
openssl x509 -in server-cert.pem -noout -subject -issuer

# Check SANs
openssl x509 -in server-cert.pem -noout -ext subjectAltName
```

### Verify Keystore

```bash
# List keystore contents
keytool -list -v -keystore keystore.jks -storepass cassandra

# Verify private key matches certificate
openssl x509 -noout -modulus -in cert.pem | openssl md5
openssl rsa -noout -modulus -in key.pem | openssl md5
# Both should output the same hash
```

---

## PEM File Support (Cassandra 4.0+)

Cassandra 4.0 introduced native PEM file support, eliminating the need for JKS or PKCS12 conversion.

### Configuration with PEM Files

```yaml
# cassandra.yaml
server_encryption_options:
    internode_encryption: all
    keystore: /etc/cassandra/certs/node-key.pem
    keystore_password: ""
    truststore: /etc/cassandra/certs/ca-chain.pem
    truststore_password: ""
```

### Combined PEM File

Create a single PEM file containing both key and certificate:

```bash
cat node-key.pem node-cert.pem > node-combined.pem
```

---

## Related Documentation

- [Encryption Overview](index.md) - Why encryption is essential
- [PKI Fundamentals](pki-fundamentals.md) - Certificate concepts
- [Hostname Verification](hostname-verification.md) - SAN configuration
- [Cassandra Configuration](configuration.md) - Using certificates in Cassandra
