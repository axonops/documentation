---
title: "Installing CQLAI"
description: "CQLAI installation guide. Install on Linux, macOS, and Windows."
meta:
  - name: keywords
    content: "CQLAI installation, install CQLAI, setup guide"
search:
  boost: 3
---

# Installing CQLAI

CQLAI is distributed as a single static binary with no dependencies. Choose the installation method that works best for the target environment.

## Quick Install

### Using Go

With Go 1.24+ installed:

```bash
go install github.com/axonops/cqlai/cmd/cqlai@latest
```

### Pre-compiled Binaries

Download the appropriate binary for your platform from [GitHub Releases](https://github.com/axonops/cqlai/releases).

**Linux (x86-64)**:
```bash
curl -L https://github.com/axonops/cqlai/releases/latest/download/cqlai-linux-amd64 -o cqlai
chmod +x cqlai
sudo mv cqlai /usr/local/bin/
```

**Linux (ARM64)**:
```bash
curl -L https://github.com/axonops/cqlai/releases/latest/download/cqlai-linux-arm64 -o cqlai
chmod +x cqlai
sudo mv cqlai /usr/local/bin/
```

**macOS (Intel)**:
```bash
curl -L https://github.com/axonops/cqlai/releases/latest/download/cqlai-darwin-amd64 -o cqlai
chmod +x cqlai
sudo mv cqlai /usr/local/bin/
```

**macOS (Apple Silicon)**:
```bash
curl -L https://github.com/axonops/cqlai/releases/latest/download/cqlai-darwin-arm64 -o cqlai
chmod +x cqlai
sudo mv cqlai /usr/local/bin/
```

**Windows**:
Download `cqlai-windows-amd64.exe` from the releases page and add it to your PATH.

---

## Package Managers

### APT (Debian/Ubuntu)

```bash
# Add AxonOps repository
curl -fsSL https://packages.axonops.com/gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/axonops-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/axonops-archive-keyring.gpg] https://packages.axonops.com/apt stable main" | sudo tee /etc/apt/sources.list.d/axonops.list

# Install CQLAI
sudo apt update
sudo apt install cqlai
```

### YUM (RHEL/CentOS/Fedora)

```bash
# Add AxonOps repository
sudo tee /etc/yum.repos.d/axonops.repo << 'EOF'
[axonops]
name=AxonOps Repository
baseurl=https://packages.axonops.com/yum
enabled=1
gpgcheck=1
gpgkey=https://packages.axonops.com/gpg.key
EOF

# Install CQLAI
sudo yum install cqlai
```

### Homebrew (macOS)

```bash
brew tap axonops/tap
brew install cqlai
```

---

## Docker

### Using Pre-built Image

```bash
# Pull the image
docker pull axonops/cqlai:latest

# Run interactively
docker run -it --rm axonops/cqlai --host your-cassandra-host
```

### With Docker Compose

Add CQLAI to a Cassandra development environment:

```yaml
version: '3.8'
services:
  cassandra:
    image: cassandra:5.0
    ports:
      - "9042:9042"

  cqlai:
    image: axonops/cqlai:latest
    depends_on:
      - cassandra
    command: ["--host", "cassandra"]
    stdin_open: true
    tty: true
```

### Build from Source (Docker)

```bash
git clone https://github.com/axonops/cqlai.git
cd cqlai
docker build -t cqlai .
docker run -it --rm cqlai --host your-cassandra-host
```

---

## Build from Source

### Prerequisites

- Go 1.24 or later
- Git

### Build Steps

```bash
# Clone the repository
git clone https://github.com/axonops/cqlai.git
cd cqlai

# Install dependencies
go mod download

# Build
go build -o cqlai cmd/cqlai/main.go

# Or use Make
make build

# Install to $GOPATH/bin
go install cmd/cqlai/main.go
```

### Development Build

For development with race detection:

```bash
make build-dev
```

---

## Verify Installation

```bash
# Check version
cqlai --version

# Show help
cqlai --help

# Test connection (requires running Cassandra)
cqlai --host 127.0.0.1
```

Expected output:
```
CQLAI v1.x.x
Modern CQL Shell for Apache Cassandra
```

---

## Supported Platforms

| Platform | Architecture | Status |
|----------|--------------|--------|
| Linux | x86-64 (amd64) | Supported |
| Linux | ARM64 (aarch64) | Supported |
| macOS | x86-64 (Intel) | Supported |
| macOS | ARM64 (Apple Silicon) | Supported |
| Windows | x86-64 | Supported |

---

## Upgrading

### Using Go

```bash
go install github.com/axonops/cqlai/cmd/cqlai@latest
```

### Using Package Manager

```bash
# APT
sudo apt update && sudo apt upgrade cqlai

# YUM
sudo yum update cqlai

# Homebrew
brew upgrade cqlai
```

### Manual Upgrade

Download the latest binary from [releases](https://github.com/axonops/cqlai/releases) and replace the existing binary.

---

## Uninstalling

### Go Installation

```bash
rm $(which cqlai)
```

### Package Manager

```bash
# APT
sudo apt remove cqlai

# YUM
sudo yum remove cqlai

# Homebrew
brew uninstall cqlai
```

### Configuration Files

CQLAI stores configuration in:
- `~/.cqlai.json` - Main configuration
- `~/.cqlai/history` - Command history
- `~/.cqlai/ai_history` - AI command history

To fully remove:
```bash
rm -rf ~/.cqlai ~/.cqlai.json
```

---

## Next Steps

After installation:

1. **[Quick Start Guide](../quickstart.md)** - Connect to Cassandra
2. **[Configuration](../configuration/index.md)** - Set up connections and AI
3. **[Commands Reference](../commands/index.md)** - Learn available commands
