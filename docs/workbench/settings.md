---
title: "Settings"
description: "Configure AxonOps Workbench settings. Theme, language, security, feature toggles, limits, and update preferences."
meta:
  - name: keywords
    content: "settings, configuration, theme, language, dark mode, updates, AxonOps Workbench"
---

# Settings

The Settings dialog in AxonOps Workbench provides centralized control over the application's appearance, security, resource limits, feature toggles, update behavior, and keyboard shortcuts. Open it from the main interface to customize the workbench to your preferences.

## Appearance

### Theme

AxonOps Workbench supports **Light** and **Dark** themes. The application can also detect your operating system's theme preference and adjust automatically.

- **Light** -- A clean, bright interface suitable for well-lit environments.
- **Dark** -- A dark interface that reduces eye strain in low-light conditions.

The workbench listens for OS-level theme changes in real time. If your system switches between light and dark mode, the application follows suit.

<!-- Screenshot: Settings dialog showing theme selection with Light and Dark options -->

### Language

The interface is available in the following languages:

| Language | Code | RTL Support |
|----------|------|-------------|
| English | `en` | No |
| Arabic - العربية | `ar` | Yes |
| Spanish | `es` | No |
| French | `fr` | No |
| Galician | `gl` | No |
| Hebrew - עִברִית | `iw` | Yes |
| Simplified Chinese - 简体中文 | `zh` | No |

Changing the language applies immediately across the entire interface without requiring a restart. For right-to-left (RTL) languages such as Arabic and Hebrew, the application automatically mirrors the layout direction.

## Security

### Logging

The logging feature records application events, processes, and errors to a log file on disk. This is valuable for troubleshooting issues or understanding application behavior.

| Setting | Default | Description |
|---------|---------|-------------|
| Logging Enabled | Disabled | When enabled, the workbench writes detailed event logs to a session log file. |

When logging is enabled, the Settings dialog displays:

- **Log file name** -- The name of the current session's log file.
- **Log folder path** -- The directory where log files are stored. In production builds, this is the system's standard application log directory. In development mode, logs are written to `data/logging/` within the application directory.

!!! tip
    Enable logging when diagnosing connection issues or unexpected behavior. You can open the log file or its containing folder directly from the Settings dialog.

### Content Protection

Content protection is an OS-level security feature that prevents the application window from being captured in screenshots or screen recordings.

| Setting | Default | Description |
|---------|---------|-------------|
| Content Protection | Disabled | When enabled, prevents screen capture tools from recording the workbench window contents. |

This feature uses the operating system's native content protection APIs. It is available on platforms that support window-level capture prevention.

!!! note
    Content protection is hidden in the Settings dialog on platforms where it is not supported.

## Limits

Resource limits control the maximum allowances for specific workbench features. Adjusting these values helps manage system resource consumption.

| Setting | Default | Description |
|---------|---------|-------------|
| Sandbox Instances | 1 | Maximum number of local Cassandra sandbox instances that can run simultaneously. |
| CQLSH Sessions | 10 | Maximum number of concurrent CQLSH sessions across all connections. |
| BLOB Insert Size | 1 MB | Maximum size of binary large objects (BLOBs) that can be inserted through the workbench interface. |

## Features

Feature toggles enable or disable specific workbench capabilities. Additional configuration options for certain features are also available in this section.

| Setting | Default | Description |
|---------|---------|-------------|
| Local Clusters | Enabled | Manage local Apache Cassandra clusters running in containers. |
| Basic CQLSH | Enabled | Access the basic CQLSH terminal interface for raw command-line interaction. |
| Preview BLOB | Enabled | Preview binary large objects (images, documents) directly within the query results. |
| AxonOps Integration | Enabled | Connect to AxonOps monitoring and management services from within the workbench. |
| Container Tool | None | Select the container management tool for local clusters: `docker`, `podman`, or `none`. |
| CQL Snippets Author Name | (empty) | Default author name embedded in the metadata of new CQL snippets. |

### Container Tool Paths

If the workbench does not automatically detect your container management tool, you can specify custom paths:

| Setting | Default | Description |
|---------|---------|-------------|
| Podman Path | (auto-detect) | Custom path to the `podman` executable. |
| Docker Path | (auto-detect) | Custom path to the `docker` executable. |

## Updates

Update settings control how the workbench checks for and installs new versions.

| Setting | Default | Description |
|---------|---------|-------------|
| Check for Updates | Enabled | Periodically check whether a new version of AxonOps Workbench is available. |
| Auto Update | Enabled | Automatically download and install updates when a new version is detected. |

The update mechanism detects your installation format and uses the appropriate update channel:

- **GitHub Releases** -- Standard builds downloaded from GitHub.
- **Mac App Store** -- macOS App Store installations.
- **Snap** -- Linux Snap package installations.
- **Flatpak** -- Linux Flatpak installations.

!!! info
    Update checking is available only in production builds. In development mode, the check-for-updates feature is disabled.

## Keyboard Shortcuts

AxonOps Workbench provides configurable keyboard shortcuts for common actions. Shortcuts that are marked as editable can be customized to your preferred key combinations. Platform-specific defaults are provided for Windows, macOS, and Linux.

| Action | Windows / Linux | macOS | Editable |
|--------|----------------|-------|----------|
| Zoom In | `Ctrl+Shift+=` | `Cmd+Shift+]` | Yes |
| Zoom Out | `Ctrl+Shift+-` | `Cmd+Shift+/` | Yes |
| Zoom Reset | `Ctrl+Shift+9` | `Cmd+Shift+9` | Yes |
| Connections Search | `Ctrl+K` | `Cmd+K` | Yes |
| Clear Enhanced Console | `Ctrl+L` | `Cmd+L` | Yes |
| Increase Basic Console Font | `Ctrl+=` | `Cmd+=` | No |
| Decrease Basic Console Font | `Ctrl+-` | `Cmd+-` | No |
| Reset Basic Console Font | `Ctrl+0` | `Cmd+0` | No |
| History Statements Forward | `Ctrl+Up` | `Cmd+Up` | Yes |
| History Statements Backward | `Ctrl+Down` | `Cmd+Down` | Yes |
| Execute CQL Statement | `Ctrl+Enter` | `Cmd+Enter` | No |
| Toggle Full Screen | `F11` | `F11` | No |
| Select Rows in Range | `Shift+Click` | `Shift+Click` | No |
| Deselect Row | `Ctrl+Click` | `Ctrl+Click` | No |

To customize an editable shortcut:

1. Open the Settings dialog and navigate to the keyboard shortcuts section.
2. Click on the shortcut you want to change.
3. Press your desired key combination.
4. The new shortcut is saved immediately.

To reset a shortcut to its default value, use the reset option next to the shortcut entry.

!!! note
    Custom shortcuts are stored locally and persist across application restarts. Shortcuts marked as non-editable are fixed and cannot be changed.

## Configuration File

All settings are stored in the `app-config.cfg` file, located in the application's `config/` directory. This file uses the INI format and can be edited directly with a text editor for advanced configuration.

**Example `app-config.cfg`:**

```ini
[security]
loggingEnabled=false
cassandraCopyrightAcknowledged=false

[ui]
theme=light
language=en

[limit]
sandbox=1
cqlsh=10
insertBlobSize=1MB

[sshtunnel]
readyTimeout=60000
forwardTimeout=60000

[features]
localClusters=true
containersManagementTool=none
basicCQLSH=true
previewBlob=true
axonOpsIntegration=true
cqlSnippetsAuthorName=

[updates]
checkForUpdates=true
autoUpdate=true

[containersManagementToolsPaths]
podman=
docker=
```

!!! warning
    Editing `app-config.cfg` manually is intended for advanced users. Incorrect values may cause unexpected behavior. Always close the application before editing the file directly, and consider creating a backup before making changes.

### Configuration Sections

| Section | Purpose |
|---------|---------|
| `[security]` | Logging toggle and acknowledgment flags |
| `[ui]` | Theme and language preferences |
| `[limit]` | Resource limits for sandbox instances, CQLSH sessions, and BLOB size |
| `[sshtunnel]` | Timeout values for SSH tunnel connections (in milliseconds) |
| `[features]` | Feature toggles and container tool selection |
| `[updates]` | Update checking and auto-update preferences |
| `[containersManagementToolsPaths]` | Custom paths for container management executables |

When the application updates, configuration files are merged automatically. New settings introduced in an update are added with their default values, while your existing preferences are preserved.
