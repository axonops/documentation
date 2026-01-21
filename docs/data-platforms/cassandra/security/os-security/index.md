---
title: "Cassandra Operating System Security"
description: "Linux operating system security for Cassandra deployments. Patching, user management, filesystem permissions, and kernel hardening."
meta:
  - name: keywords
    content: "Cassandra OS security, Linux hardening, patching, filesystem security, user management"
search:
  boost: 3
---

# Operating System Security

Cassandra's security depends on the underlying operating system. A compromised OS grants full access to data files, configuration, and credentials regardless of Cassandra-level security controls. This guide covers Linux security practices essential for production Cassandra deployments.

---

## Security Hardening Frameworks

### CIS Benchmarks

The Center for Internet Security (CIS) publishes consensus-based security configuration guidelines. CIS Benchmarks provide prescriptive hardening standards with specific configuration values.

#### Relevant CIS Benchmarks

| Benchmark | Applicability |
|-----------|---------------|
| CIS Red Hat Enterprise Linux 8/9 | RHEL-based Cassandra hosts |
| CIS Ubuntu Linux 22.04/24.04 LTS | Ubuntu-based Cassandra hosts |
| CIS Amazon Linux 2/2023 | AWS EC2 deployments |
| CIS Oracle Linux 8/9 | Oracle Cloud deployments |
| CIS Distribution Independent Linux | General Linux guidance |

#### CIS Profile Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| Level 1 | Essential security settings, minimal performance impact | Production baseline |
| Level 2 | Defense-in-depth, may reduce functionality | High-security environments |
| STIG | Aligned with DISA STIG requirements | Government/DoD systems |

#### Key CIS Controls for Cassandra Hosts

**Section 1 – Initial Setup**

| Control | Recommendation | Cassandra Notes |
|---------|----------------|-----------------|
| 1.1.x | Filesystem configuration | Separate partitions for `/var/lib/cassandra` |
| 1.4.x | Secure boot settings | UEFI Secure Boot where supported |
| 1.5.x | Process hardening | ASLR, core dump restrictions |

**Section 2 – Services**

| Control | Recommendation | Cassandra Notes |
|---------|----------------|-----------------|
| 2.1.x | Remove unnecessary services | Disable X11, CUPS, Avahi |
| 2.2.x | Disable unnecessary clients | Remove FTP, telnet clients |

**Section 3 – Network Configuration**

| Control | Recommendation | Cassandra Notes |
|---------|----------------|-----------------|
| 3.1.x | Disable unused network protocols | Disable DCCP, SCTP, RDS |
| 3.2.x | Network parameters (host) | IP forwarding, ICMP redirects |
| 3.4.x | Firewall configuration | Restrict to Cassandra ports only |

**Section 4 – Logging and Auditing**

| Control | Recommendation | Cassandra Notes |
|---------|----------------|-----------------|
| 4.1.x | Configure auditd | Log Cassandra file access |
| 4.2.x | Configure logging | Centralize logs, protect integrity |

**Section 5 – Access, Authentication, Authorization**

| Control | Recommendation | Cassandra Notes |
|---------|----------------|-----------------|
| 5.2.x | SSH configuration | Key-based auth, no root login |
| 5.3.x | PAM configuration | Password complexity, lockout |
| 5.4.x | User accounts | Service account restrictions |
| 5.5.x | Root login restrictions | Limit root access methods |

**Section 6 – System Maintenance**

| Control | Recommendation | Cassandra Notes |
|---------|----------------|-----------------|
| 6.1.x | File permissions | Cassandra data/config permissions |
| 6.2.x | User and group settings | Verify cassandra user configuration |

#### Automated CIS Assessment

```bash
# CIS-CAT Pro (commercial)
./Assessor-CLI.sh -b benchmarks/CIS_Red_Hat_Enterprise_Linux_9_Benchmark_v1.0.0.xml

# OpenSCAP (open source)
sudo yum install scap-security-guide openscap-scanner
sudo oscap xccdf eval --profile cis \
    --results results.xml \
    --report report.html \
    /usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml

# Lynis (open source)
sudo lynis audit system --profile server
```

### DISA STIGs

Defense Information Systems Agency (DISA) Security Technical Implementation Guides (STIGs) provide security hardening standards required for U.S. Department of Defense systems.

#### STIG vs CIS Comparison

| Aspect | CIS Benchmarks | DISA STIGs |
|--------|----------------|------------|
| Authority | Industry consensus | U.S. DoD mandate |
| Scope | General best practice | DoD/government compliance |
| Severity | Levels 1, 2 | CAT I, II, III |
| Format | PDF, automated tools | XCCDF, manual checklists |
| Updates | Quarterly | As needed |
| Cost | Free (benchmarks), paid (tools) | Free |

#### STIG Severity Categories

| Category | Description | Remediation Timeline |
|----------|-------------|---------------------|
| CAT I | High severity, direct exploitation risk | Immediate |
| CAT II | Medium severity, potential for exploitation | Within 30 days |
| CAT III | Low severity, defense-in-depth | Within 90 days |

#### Relevant STIGs

| STIG | Version | Application |
|------|---------|-------------|
| Red Hat Enterprise Linux 8/9 STIG | Current | RHEL hosts |
| Ubuntu 20.04/22.04 STIG | Current | Ubuntu hosts |
| General Purpose Operating System STIG | Current | All Linux |
| Application Security and Development STIG | Current | Cassandra application |

#### Key STIG Requirements for Database Hosts

**Authentication (SRG-OS-000xxx)**

```bash
# V-230332: Lock accounts after 3 failed attempts
# /etc/security/faillock.conf
deny = 3
unlock_time = 900
fail_interval = 900

# V-230340: Password minimum length
# /etc/security/pwquality.conf
minlen = 15
```

**Access Control (SRG-OS-000xxx)**

```bash
# V-230386: Set permissions on /etc/passwd
chmod 644 /etc/passwd

# V-230388: Set permissions on /etc/shadow
chmod 000 /etc/shadow

# V-230483: Disable core dumps for SUID programs
echo '* hard core 0' >> /etc/security/limits.conf
echo 'fs.suid_dumpable = 0' >> /etc/sysctl.d/99-stig.conf
```

**Audit and Accountability (SRG-OS-000xxx)**

```bash
# V-230398: Audit privileged commands
-a always,exit -F path=/usr/bin/sudo -F perm=x -F auid>=1000 -F auid!=unset -k priv_cmd

# V-230402: Audit file deletions
-a always,exit -F arch=b64 -S unlink,unlinkat,rename,renameat -F auid>=1000 -F auid!=unset -k delete
```

**System Integrity (SRG-OS-000xxx)**

```bash
# V-230222: Enable FIPS mode (if required)
fips-mode-setup --enable

# V-230264: Install AIDE for file integrity
sudo yum install aide
sudo aide --init
```

#### STIG Assessment Tools

```bash
# SCAP Compliance Checker (SCC)
# Download from DoD Cyber Exchange: https://public.cyber.mil/stigs/scap/
./scc -u /path/to/stig-benchmark.xml

# OpenSCAP with STIG profile
sudo oscap xccdf eval --profile stig \
    --results stig-results.xml \
    --report stig-report.html \
    /usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml

# Ansible STIG roles
ansible-galaxy install RedHatOfficial.rhel9_stig
ansible-playbook -i inventory stig-playbook.yml
```

### Framework Exceptions for Cassandra

Some hardening controls may conflict with Cassandra requirements. Document exceptions with compensating controls:

| Control | Conflict | Compensating Control |
|---------|----------|---------------------|
| Disable IPv6 | May be needed for cluster | Firewall IPv6, use IPv4 for Cassandra |
| noexec on /tmp | JVM may use /tmp for JIT | Use dedicated Java temp directory |
| Strict umask | Cassandra file sharing | Set umask in cassandra-env.sh |
| Password expiration | Service accounts | Use locked accounts, no password auth |
| Session timeout | Long-running repairs | Exclude cassandra processes |

```bash
# Configure Java to use dedicated temp directory
# cassandra-env.sh
JVM_OPTS="$JVM_OPTS -Djava.io.tmpdir=/var/lib/cassandra/tmp"
```

```bash
# Create dedicated temp directory
sudo mkdir -p /var/lib/cassandra/tmp
sudo chown cassandra:cassandra /var/lib/cassandra/tmp
sudo chmod 750 /var/lib/cassandra/tmp
```

---

## Regulatory Compliance and Patching

### Compliance Requirements

Most regulatory frameworks mandate timely patching of security vulnerabilities:

| Framework | Patching Requirement |
|-----------|---------------------|
| PCI DSS 4.0 | Requirement 6.3.3: Critical patches within 30 days |
| SOC 2 | CC6.1: Logical and physical access controls including patch management |
| HIPAA | §164.308(a)(5)(ii)(B): Protection from malicious software |
| CIS Controls | Control 7: Continuous vulnerability management |
| NIST 800-53 | SI-2: Flaw remediation |

### Patch Management Strategy

#### Vulnerability Severity Classification

| Severity | CVSS Score | Response Time | Action |
|----------|------------|---------------|--------|
| Critical | 9.0 – 10.0 | 24-72 hours | Emergency patch window |
| High | 7.0 – 8.9 | 7-14 days | Priority scheduling |
| Medium | 4.0 – 6.9 | 30 days | Standard maintenance |
| Low | 0.1 – 3.9 | 90 days | Next scheduled window |

#### Patching Process

```bash
# 1. Check available security updates
sudo yum check-update --security    # RHEL/CentOS
sudo apt list --upgradable          # Debian/Ubuntu

# 2. Review CVEs affecting installed packages
sudo yum updateinfo list security
sudo apt-get changelog <package>

# 3. Test in non-production first
# Apply patches to staging environment
# Run integration tests
# Verify Cassandra functionality

# 4. Apply to production (rolling)
# One node at a time
nodetool drain
sudo systemctl stop cassandra
sudo yum update --security -y
sudo systemctl start cassandra
# Wait for node to rejoin and stream
nodetool status
```

#### Automated Security Updates

```bash
# /etc/yum/yum-cron.conf (RHEL/CentOS)
[commands]
update_cmd = security
apply_updates = yes

# Exclude Cassandra packages from auto-update
# (manual control for database software)
[base]
exclude = cassandra* java*
```

```bash
# /etc/apt/apt.conf.d/50unattended-upgrades (Debian/Ubuntu)
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};

# Blacklist database packages
Unattended-Upgrade::Package-Blacklist {
    "cassandra";
    "openjdk-";
};
```

---

## User and Access Security

### Dedicated Service Account

Cassandra should run under a dedicated unprivileged user account:

```bash
# Create cassandra user (if not created by package)
sudo groupadd -r cassandra
sudo useradd -r -g cassandra -d /var/lib/cassandra -s /sbin/nologin cassandra

# Verify account properties
id cassandra
# uid=xxx(cassandra) gid=xxx(cassandra) groups=xxx(cassandra)

# Ensure no login shell
grep cassandra /etc/passwd
# cassandra:x:xxx:xxx::/var/lib/cassandra:/sbin/nologin
```

#### Account Security Properties

| Property | Recommended Setting | Purpose |
|----------|-------------------|---------|
| Shell | `/sbin/nologin` or `/bin/false` | Prevent interactive login |
| Home directory | `/var/lib/cassandra` | Contain data access |
| Password | Locked (`!` or `*`) | Prevent password authentication |
| System account | `-r` flag | UID below 1000 |

### Privilege Separation

```bash
# Lock the cassandra account password
sudo passwd -l cassandra

# Verify account is locked
sudo passwd -S cassandra
# cassandra L 2024-01-15 0 99999 7 -1 (Password locked.)

# Remove from any unnecessary groups
sudo gpasswd -d cassandra wheel 2>/dev/null || true
```

### SSH Access Controls

```bash
# /etc/ssh/sshd_config

# Disable root login
PermitRootLogin no

# Deny cassandra service account SSH access
DenyUsers cassandra

# Restrict SSH to specific users/groups
AllowGroups sysadmins dba-team

# Disable password authentication (use keys)
PasswordAuthentication no
PubkeyAuthentication yes

# Set idle timeout
ClientAliveInterval 300
ClientAliveCountMax 2

# Restrict SSH protocol
Protocol 2
```

```bash
# Apply SSH configuration
sudo systemctl reload sshd
```

### Sudo Configuration

```bash
# /etc/sudoers.d/cassandra-admin

# Allow DBA team to manage Cassandra service
%dba-team ALL=(ALL) /usr/bin/systemctl start cassandra
%dba-team ALL=(ALL) /usr/bin/systemctl stop cassandra
%dba-team ALL=(ALL) /usr/bin/systemctl restart cassandra
%dba-team ALL=(ALL) /usr/bin/systemctl status cassandra
%dba-team ALL=(ALL) /usr/bin/nodetool *
%dba-team ALL=(ALL) /usr/bin/cqlsh

# Require password for sudo
Defaults:%dba-team timestamp_timeout=5

# Log all sudo commands
Defaults log_output
Defaults!/usr/bin/sudoreplay !log_output
```

---

## Filesystem Security

### Directory Ownership and Permissions

```bash
# Cassandra directories
sudo chown -R cassandra:cassandra /var/lib/cassandra
sudo chown -R cassandra:cassandra /var/log/cassandra
sudo chown -R root:cassandra /etc/cassandra

# Permissions
sudo chmod 750 /var/lib/cassandra
sudo chmod 750 /var/log/cassandra
sudo chmod 750 /etc/cassandra

# Data directories
sudo chmod 700 /var/lib/cassandra/data
sudo chmod 700 /var/lib/cassandra/commitlog
sudo chmod 700 /var/lib/cassandra/saved_caches
sudo chmod 700 /var/lib/cassandra/hints

# Configuration files
sudo chmod 640 /etc/cassandra/cassandra.yaml
sudo chmod 640 /etc/cassandra/cassandra-env.sh
sudo chmod 600 /etc/cassandra/jmxremote.password
```

#### Permission Reference

| Path | Owner | Group | Mode | Notes |
|------|-------|-------|------|-------|
| `/var/lib/cassandra` | cassandra | cassandra | 750 | Data root |
| `/var/lib/cassandra/data` | cassandra | cassandra | 700 | SSTable data |
| `/var/lib/cassandra/commitlog` | cassandra | cassandra | 700 | Commit logs |
| `/var/log/cassandra` | cassandra | cassandra | 750 | Log files |
| `/etc/cassandra` | root | cassandra | 750 | Configuration |
| `/etc/cassandra/cassandra.yaml` | root | cassandra | 640 | Main config |
| `/etc/cassandra/*.password` | root | cassandra | 600 | Credentials |

### Mount Options

```bash
# /etc/fstab

# Data volume - noexec prevents binary execution
/dev/sdb1 /var/lib/cassandra ext4 defaults,noexec,nodev,nosuid 0 2

# Log volume
/dev/sdc1 /var/log/cassandra ext4 defaults,noexec,nodev,nosuid 0 2
```

| Mount Option | Purpose |
|--------------|---------|
| `noexec` | Prevent execution of binaries on data volumes |
| `nodev` | Prevent device file interpretation |
| `nosuid` | Ignore setuid/setgid bits |

### File Integrity Monitoring

```bash
# AIDE (Advanced Intrusion Detection Environment)
sudo yum install aide

# /etc/aide.conf
/etc/cassandra CONTENT_EX
/var/lib/cassandra/data DATAONLY
!/var/lib/cassandra/commitlog
!/var/lib/cassandra/saved_caches

# Initialize database
sudo aide --init
sudo mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz

# Check for changes
sudo aide --check
```

---

## Kernel Security

### Security-Related Sysctl Settings

```bash
# /etc/sysctl.d/99-cassandra-security.conf

# Network security
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1
net.ipv4.tcp_syncookies = 1

# Disable IPv6 if not needed
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1

# Memory protection
kernel.randomize_va_space = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2

# Core dump restrictions
fs.suid_dumpable = 0
kernel.core_pattern = |/bin/false
```

```bash
# Apply settings
sudo sysctl --system
```

### Resource Limits

```bash
# /etc/security/limits.d/cassandra.conf

# File descriptors (required for Cassandra)
cassandra soft nofile 1048576
cassandra hard nofile 1048576

# Process limits
cassandra soft nproc 32768
cassandra hard nproc 32768

# Memory lock (for JVM)
cassandra soft memlock unlimited
cassandra hard memlock unlimited

# Address space
cassandra soft as unlimited
cassandra hard as unlimited
```

### Core Dump Management

```bash
# Disable core dumps globally
echo '* hard core 0' >> /etc/security/limits.conf

# Or restrict to specific directory with proper permissions
# /etc/sysctl.d/99-coredump.conf
kernel.core_pattern = /var/crash/core.%e.%p.%t
```

```bash
# Secure core dump directory if enabled
sudo mkdir -p /var/crash
sudo chmod 700 /var/crash
```

---

## SELinux / AppArmor

### SELinux and Cassandra

!!! warning "SELinux Compatibility"
    SELinux in enforcing mode frequently causes issues with Cassandra. There is no official SELinux policy module for Cassandra, and the JVM's dynamic behavior (JIT compilation, memory-mapped files, native library loading) conflicts with SELinux's access control model.

#### Recommended Approach

Most production Cassandra deployments use one of these approaches:

| Mode | Setting | Use Case |
|------|---------|----------|
| Permissive | `setenforce 0` | Log violations without blocking (recommended for most) |
| Disabled | `SELINUX=disabled` | Simpler operations, use other compensating controls |
| Enforcing | `setenforce 1` | Only if mandated by compliance (requires significant effort) |

```bash
# Check current status
getenforce
sestatus

# Set to permissive (immediate, non-persistent)
sudo setenforce 0

# Set to permissive (persistent)
sudo sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
```

#### Compensating Controls When SELinux is Disabled/Permissive

If SELinux is not in enforcing mode, implement these compensating controls:

| Control | Purpose |
|---------|---------|
| Filesystem permissions | Restrict access to Cassandra directories |
| Dedicated service account | Run Cassandra as unprivileged user |
| Firewall rules | Limit network access to required ports |
| auditd rules | Monitor file access and process execution |
| systemd hardening | Use ProtectSystem, PrivateTmp, NoNewPrivileges |

#### Enforcing Mode (If Required)

For environments where SELinux enforcing mode is mandated, expect significant troubleshooting. A custom policy must be developed iteratively:

```bash
# 1. Start in permissive mode to collect denials
sudo setenforce 0

# 2. Start Cassandra and exercise all functionality
sudo systemctl start cassandra
# Run repairs, backups, streaming, etc.

# 3. Generate policy from collected denials
sudo grep cassandra /var/log/audit/audit.log | audit2allow -M cassandra-local
sudo semodule -i cassandra-local.pp

# 4. Test in enforcing mode
sudo setenforce 1
sudo systemctl restart cassandra

# 5. Repeat steps 2-4 until all operations work
```

Common denial categories requiring policy rules:

| Denial Type | Cause |
|-------------|-------|
| `mmap_file` | JVM memory-mapped files |
| `execmem` | JIT compilation |
| `name_bind` | Binding to ports 7000, 7001, 9042 |
| `file write` | SSTable creation, commit logs |
| `unix_stream_socket` | Internal JVM communication |

### AppArmor (Ubuntu/Debian)

```bash
# /etc/apparmor.d/usr.sbin.cassandra

#include <tunables/global>

/usr/sbin/cassandra {
  #include <abstractions/base>
  #include <abstractions/java>

  # Binary and libraries
  /usr/share/cassandra/** r,
  /usr/share/cassandra/lib/*.jar r,

  # Configuration
  /etc/cassandra/ r,
  /etc/cassandra/** r,

  # Data directories
  /var/lib/cassandra/ rw,
  /var/lib/cassandra/** rwk,

  # Logs
  /var/log/cassandra/ rw,
  /var/log/cassandra/** rw,

  # Temp
  /tmp/ r,
  /tmp/cassandra-* rwk,

  # Network
  network inet stream,
  network inet dgram,

  # Java
  /usr/lib/jvm/** mr,
  /proc/*/fd/ r,
  /proc/sys/vm/max_map_count r,
}
```

```bash
# Load profile
sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.cassandra
sudo aa-enforce /usr/sbin/cassandra
```

---

## Audit Framework

### Auditd Configuration

```bash
# /etc/audit/rules.d/cassandra.rules

# Monitor Cassandra configuration changes
-w /etc/cassandra/ -p wa -k cassandra_config

# Monitor Cassandra data directory access
-w /var/lib/cassandra/ -p wa -k cassandra_data

# Monitor Cassandra binary execution
-w /usr/share/cassandra/bin/ -p x -k cassandra_exec

# Monitor authentication files
-w /etc/cassandra/jmxremote.password -p rwa -k cassandra_auth
-w /etc/cassandra/jmxremote.access -p rwa -k cassandra_auth

# Monitor user/group changes
-w /etc/passwd -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/shadow -p wa -k identity

# Monitor sudo usage
-w /etc/sudoers -p wa -k sudoers
-w /etc/sudoers.d/ -p wa -k sudoers

# Log all commands run by cassandra user
-a always,exit -F arch=b64 -F euid=cassandra -S execve -k cassandra_commands
```

```bash
# Load audit rules
sudo augenrules --load
sudo systemctl restart auditd

# Search audit logs
sudo ausearch -k cassandra_config
sudo ausearch -k cassandra_auth -ts today
```

### Log Forwarding

```bash
# /etc/rsyslog.d/cassandra.conf

# Forward audit logs to central SIEM
if $programname == 'audit' then @@siem.example.com:514

# Forward Cassandra logs
$ModLoad imfile
$InputFileName /var/log/cassandra/system.log
$InputFileTag cassandra:
$InputFileStateFile cassandra-system-log
$InputFileSeverity info
$InputFileFacility local0
$InputRunFileMonitor

local0.* @@siem.example.com:514
```

---

## Service Hardening

### Systemd Service Configuration

```ini
# /etc/systemd/system/cassandra.service.d/security.conf

[Service]
# Run as unprivileged user
User=cassandra
Group=cassandra

# Restrict filesystem access
ProtectSystem=full
ProtectHome=true
ReadWritePaths=/var/lib/cassandra /var/log/cassandra
ReadOnlyPaths=/etc/cassandra

# Restrict kernel access
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

# Restrict device access
PrivateDevices=true

# Disable privilege escalation
NoNewPrivileges=true

# Restrict capabilities
CapabilityBoundingSet=CAP_NET_BIND_SERVICE CAP_IPC_LOCK
AmbientCapabilities=CAP_NET_BIND_SERVICE CAP_IPC_LOCK

# Restrict system calls (may need tuning)
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM

# Private temp directory
PrivateTmp=true

# Restrict network
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX

# Limit resources
LimitNOFILE=1048576
LimitNPROC=32768
LimitMEMLOCK=infinity
```

```bash
# Reload systemd
sudo systemctl daemon-reload
sudo systemctl restart cassandra
```

---

## Security Hardening Checklist

### Pre-Deployment

- [ ] OS installed from verified media
- [ ] Minimal installation (no GUI, unnecessary packages removed)
- [ ] All security patches applied
- [ ] Dedicated service account created
- [ ] SSH hardened (keys only, root disabled)
- [ ] Firewall configured

### Filesystem

- [ ] Separate partitions for data, logs, OS
- [ ] Correct ownership and permissions
- [ ] Mount options applied (noexec, nodev, nosuid)
- [ ] File integrity monitoring configured

### Access Control

- [ ] Sudo configured with least privilege
- [ ] Service account locked
- [ ] SELinux permissive/disabled with compensating controls (or enforcing if mandated)
- [ ] Audit logging enabled

### Ongoing

- [ ] Automated security updates (OS packages)
- [ ] Vulnerability scanning scheduled
- [ ] Audit logs reviewed
- [ ] Access reviews performed
- [ ] Patch compliance monitored

---

## Related Documentation

- **[Security Overview](../index.md)** - Cassandra security guide
- **[Network Security](../network/index.md)** - Firewall and network configuration
- **[Audit Logging](../audit-logging/index.md)** - Cassandra audit logging
- **[Authentication](../authentication/index.md)** - User authentication
