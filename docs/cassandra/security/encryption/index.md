# Encryption

Transport Layer Security (TLS) provides encryption for data in transit between Cassandra nodes and between clients and the cluster. This documentation covers the cryptographic concepts, implementation details, and enterprise configuration requirements for securing Cassandra communications.

## Why Encryption Is Essential

A common misconception in enterprise environments is that database clusters deployed within private networks are inherently secure. This assumption creates significant risk exposure.

### The False Security of Network Isolation

Deployments relying solely on network perimeter security face the following vulnerabilities:

**Lateral Movement Attacks**
Once an attacker gains access to any system within the network perimeter, unencrypted database traffic becomes visible. Network sniffing tools can capture authentication credentials, query content, and data in transit. A compromised application server or developer workstation provides sufficient access to intercept Cassandra traffic.

**Insider Threats**
Personnel with network access—system administrators, network engineers, contractors—can passively monitor unencrypted traffic without detection. Regulatory frameworks such as SOC 2, HIPAA, and PCI-DSS recognize this risk and mandate encryption regardless of network topology.

**Man-in-the-Middle Attacks**
Without TLS, attackers with network access can intercept and modify traffic between nodes or between clients and the cluster. ARP spoofing, DNS hijacking, or compromised network equipment can redirect traffic through attacker-controlled systems.

**Data Exfiltration Detection**
Encrypted traffic with proper certificate validation makes unauthorized data access detectable. When certificates are required, unauthorized clients cannot establish connections, and connection attempts are logged.

### Compliance Requirements

| Standard | Encryption Requirement |
|----------|----------------------|
| PCI-DSS | Encrypt cardholder data in transit across open networks; strongly recommended for internal networks |
| HIPAA | Addressable requirement for ePHI; encryption provides safe harbor in breach scenarios |
| SOC 2 | Common Criteria CC6.7 requires encryption of data in transit |
| GDPR | Article 32 mandates "appropriate technical measures" including encryption |
| FedRAMP | Mandatory encryption for all data in transit |

### Enterprise Security Posture

Organizations should implement TLS encryption as a baseline security control, not as an optional enhancement. The operational overhead of certificate management is minimal compared to the risk exposure of unencrypted database traffic.

---

## Encryption Types

Cassandra provides two separate encryption configurations:

| Configuration | Scope | Traffic Protected |
|---------------|-------|-------------------|
| `client_encryption_options` | Client-to-node | CQL queries, results, authentication |
| `server_encryption_options` | Node-to-node | Gossip, streaming, repair, inter-node queries |

### Encryption Mode Reference

| Mode | Same Rack | Same DC | Cross-DC | Use Case |
|------|-----------|---------|----------|----------|
| none | Plain | Plain | Plain | Development only |
| rack | Plain | Encrypted | Encrypted | Physical rack security |
| dc | Plain | Plain | Encrypted | Cross-DC WAN encryption |
| all | Encrypted | Encrypted | Encrypted | Recommended for production |

---

## Documentation Structure

This encryption documentation is organized into the following sections:

| Section | Description |
|---------|-------------|
| [PKI Fundamentals](pki-fundamentals.md) | Public Key Infrastructure concepts, certificates, and trust |
| [TLS Versions](tls-versions.md) | TLS protocol versions, cipher suites, and security status |
| [Certificate Types](certificates.md) | Server certificates, client certificates, and CA configuration |
| [Hostname Verification](hostname-verification.md) | Identity verification and Subject Alternative Names |
| [Cassandra Configuration](configuration.md) | Server and client encryption settings in cassandra.yaml |
| [Client Configuration](client-configuration.md) | cqlsh, Java driver, and application configuration |
| [Enterprise Recommendations](enterprise-recommendations.md) | Certificate lifecycle, security hardening, and best practices |
| [Troubleshooting](troubleshooting.md) | Common issues and resolution procedures |

---

## Quick Start

For a minimal TLS configuration:

1. [Generate certificates](certificates.md#certificate-generation) for each node
2. [Configure server encryption](configuration.md#internode-encryption) in cassandra.yaml
3. [Configure client encryption](configuration.md#client-encryption) in cassandra.yaml
4. [Configure clients](client-configuration.md) to use TLS

For production deployments, review the [Enterprise Recommendations](enterprise-recommendations.md) for certificate lifecycle management and security hardening.

---

## Related Documentation

- [Security Overview](../index.md) - Security architecture
- [Authentication](../authentication/index.md) - User authentication
- [Authorization](../authorization/index.md) - Access control

---

## Version Information

| Feature | Cassandra Version |
|---------|------------------|
| Basic TLS Support | All versions |
| PEM file support | 4.0+ |
| Hot reloading of certificates | 4.0+ |
| Hostname verification option | 4.0+ |
| TLS 1.3 support | 4.0+ (requires Java 11+) |
