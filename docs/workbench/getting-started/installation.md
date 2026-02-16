---
title: "Installation"
description: "Download and install AxonOps Workbench on macOS, Windows, or Linux. System requirements and installation instructions."
meta:
  - name: keywords
    content: "install AxonOps Workbench, download, macOS, Windows, Linux, Homebrew, system requirements"
---

# Installation

AxonOps Workbench is available for macOS, Windows, and Linux. This page covers system requirements, download options, and step-by-step installation instructions for each platform.

---

## System Requirements

| Requirement | Details |
|-------------|---------|
| **macOS** | macOS 12 (Monterey) or later |
| **Windows** | Windows 10 or later |
| **Linux** | Ubuntu 20.04+, Fedora 36+, RHEL 8+, or equivalent |
| **Architecture** | x64 (Intel/AMD) on all platforms; arm64 (Apple Silicon) on macOS and Linux |
| **Disk Space** | ~400 MB |
| **RAM** | 4 GB minimum, 8 GB recommended |

!!! info "Node.js is bundled"
    AxonOps Workbench ships with Node.js built in. You do not need to install Node.js separately.

---

## Download

You can download AxonOps Workbench from either of these locations:

- [AxonOps Workbench download page](https://axonops.com/workbench/download/){:target="_blank"} -- recommended for stable releases
- [GitHub Releases](https://github.com/axonops/axonops-workbench-cassandra/releases){:target="_blank"} -- all releases including pre-release builds

### Available Formats

| Platform | Formats |
|----------|---------|
| **macOS** | DMG, ZIP |
| **Windows** | NSIS installer (.exe), MSI installer |
| **Linux** | tar.gz, DEB, RPM, AppImage, Snap, Flatpak |

---

## macOS

### Option 1: Direct Download (DMG)

1. Download the `.dmg` file for your architecture from the [download page](https://axonops.com/workbench/download/){:target="_blank"}:

    - **Apple Silicon** (M1/M2/M3/M4): `AxonOps.Workbench-<version>-mac-arm64.dmg`
    - **Intel**: `AxonOps.Workbench-<version>-mac-x64.dmg`

2. Open the downloaded `.dmg` file.
3. Drag **AxonOps Workbench** into your **Applications** folder.
4. Eject the disk image.
5. Launch AxonOps Workbench from your Applications folder or Spotlight.

!!! note "macOS Gatekeeper"
    On first launch, macOS may display a security prompt because the application was downloaded from the internet. Click **Open** to proceed. AxonOps Workbench is signed and notarized by Apple.

### Option 2: Homebrew

If you use [Homebrew](https://brew.sh/){:target="_blank"}, install AxonOps Workbench with:

```bash
brew tap axonops/homebrew-repository
brew install --cask axonopsworkbench
```

To install a beta release instead:

```bash
brew install --cask axonopsworkbench-beta
```

!!! tip "Custom Applications directory"
    To install into your home Applications folder instead of the system-wide one, set the `HOMEBREW_CASK_OPTS` environment variable before installing:

    ```bash
    export HOMEBREW_CASK_OPTS="--appdir=~/Applications"
    ```

---

## Windows

### Option 1: NSIS Installer (Recommended)

1. Download the `.exe` installer from the [download page](https://axonops.com/workbench/download/){:target="_blank"}:

    - `AxonOps.Workbench-<version>-win-x64.exe`

2. Run the installer and follow the on-screen prompts.
3. Choose the installation directory (the default is recommended).
4. Once installation completes, launch AxonOps Workbench from the Start menu or desktop shortcut.

!!! note "Windows SmartScreen"
    Windows may display a SmartScreen warning on first run. Click **More info** and then **Run anyway** to proceed.

### Option 2: MSI Installer

The MSI installer is available for environments that require MSI-based deployment (such as Group Policy or SCCM):

1. Download `AxonOps.Workbench-<version>-win-x64.msi` from the [download page](https://axonops.com/workbench/download/){:target="_blank"}.
2. Run the `.msi` file and follow the installation wizard.

---

## Linux

AxonOps Workbench supports multiple Linux packaging formats. Choose the one that best suits your distribution.

### Debian / Ubuntu (DEB)

Download the `.deb` package and install it with `apt`:

```bash
sudo apt install ./AxonOps.Workbench-<version>-linux-amd64.deb
```

This automatically resolves dependencies including `libnss3` and `libsecret-1-0`.

To uninstall:

```bash
sudo apt remove axonops-workbench
```

### Red Hat / Fedora (RPM)

Download the `.rpm` package and install it with `dnf`:

```bash
sudo dnf install ./AxonOps.Workbench-<version>-linux-x86_64.rpm
```

On older systems using `yum`:

```bash
sudo yum install ./AxonOps.Workbench-<version>-linux-x86_64.rpm
```

To uninstall:

```bash
sudo dnf remove axonops-workbench
```

### Manual Install (tar.gz)

The portable tar.gz archive works on any Linux distribution:

1. Download the `.tar.gz` archive for your architecture:

    - **x64**: `AxonOps.Workbench-<version>-linux-x64.tar.gz`
    - **arm64**: `AxonOps.Workbench-<version>-linux-arm64.tar.gz`

2. Extract the archive:

    ```bash
    tar -xzf AxonOps.Workbench-<version>-linux-x64.tar.gz
    ```

3. Run the application:

    ```bash
    ./axonops-workbench/axonops-workbench --no-sandbox
    ```

!!! tip "Desktop integration"
    For a more integrated experience, move the extracted folder to `/opt` and create a `.desktop` file in `~/.local/share/applications/`.

### Snap Store

Install AxonOps Workbench from the Snap Store:

```bash
sudo snap install axonops-workbench
```

### Flatpak

Install AxonOps Workbench via Flatpak:

```bash
flatpak install axonops-workbench
```

### AppImage

The AppImage format provides a portable, single-file executable:

1. Download the `.AppImage` file from the [GitHub Releases](https://github.com/axonops/axonops-workbench-cassandra/releases){:target="_blank"} page.
2. Make it executable:

    ```bash
    chmod +x AxonOps.Workbench-<version>-linux-x86_64.AppImage
    ```

3. Run the application:

    ```bash
    ./AxonOps.Workbench-<version>-linux-x86_64.AppImage
    ```

---

## Verifying the Download

Each release on [GitHub Releases](https://github.com/axonops/axonops-workbench-cassandra/releases){:target="_blank"} includes SHA256 checksums. Verify your download to ensure it has not been tampered with or corrupted during transfer.

**macOS / Linux:**

```bash
sha256sum AxonOps.Workbench-<version>-<os>-<arch>.<ext>
```

Compare the output against the checksum published on the release page.

**Windows (PowerShell):**

```bash
Get-FileHash AxonOps.Workbench-<version>-win-x64.exe -Algorithm SHA256
```

!!! info "Software Bill of Materials"
    Each release also includes SBOM files in CycloneDX and SPDX formats for supply chain transparency. These are available as release artifacts on GitHub.

---

## First Launch

After installation, launch AxonOps Workbench and you will be greeted with the welcome screen. From there you can create your first workspace and set up a connection to a Cassandra cluster.

For a guided walkthrough of the initial setup, see the [First Steps](first-steps.md) guide.
