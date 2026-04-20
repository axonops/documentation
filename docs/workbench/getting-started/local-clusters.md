---
title: "Local Clusters"
description: "Create local Cassandra clusters with Docker or Podman directly from AxonOps Workbench. One-click development environments."
meta:
  - name: keywords
    content: "local clusters, Docker, Podman, Cassandra development, sandbox, AxonOps Workbench"
---

# Local Clusters

AxonOps Workbench lets you create fully functional Apache Cassandra clusters on your local machine with a single click. These local clusters run as Docker or Podman containers, giving you an isolated development and testing environment without the overhead of provisioning remote infrastructure.

Each local cluster is a self-contained sandbox project powered by Docker Compose. You can spin up multi-node Cassandra clusters, optionally include AxonOps monitoring, and connect to them directly from the Workbench query editor -- all without leaving the application.

---

## Prerequisites

Before creating a local cluster, you need a container runtime installed on your machine.

| Requirement | Details |
|-------------|---------|
| **Container Runtime** | [Docker Desktop](https://docs.docker.com/get-docker/){:target="_blank"} or [Podman](https://podman.io/getting-started/installation){:target="_blank"} |
| **Docker Compose** | Included with Docker Desktop. For Podman, install [podman-compose](https://github.com/containers/podman-compose){:target="_blank"} separately. |
| **Disk Space** | At least 2 GB free (more for multi-node clusters with monitoring) |
| **RAM** | 4 GB minimum available for containers; 8 GB or more recommended for multi-node clusters |

!!! warning "Local development only"
    Local clusters are intended for development and testing purposes. They are not suitable for production workloads.

!!! note "Linux users"
    When using Docker on Linux, your user account must belong to the `docker` group. You can add yourself with:

    ```bash
    sudo usermod -aG docker $USER
    ```

    Log out and back in for the change to take effect. This requirement does not apply when using Podman.

---

## Container Tool Setup

AxonOps Workbench supports both Docker and Podman as container management tools. You select which tool to use when creating your first local cluster, and you can change it at any time in the application settings.

### Selecting a Tool During Cluster Creation

When you open the **Create Local Cluster** dialog, you are prompted to select either **Docker** or **Podman** as the container management tool. This selection is saved and used for all subsequent operations.

### Changing the Tool in Settings

To change your container management tool after initial setup:

1. Open the application **Settings**.
2. Navigate to the **Features** section.
3. Under **Container Management Tool**, select **Docker** or **Podman**.

### Custom Binary Paths

If your container tool is installed in a non-standard location, you can specify the path manually:

1. Open the application **Settings**.
2. Look for the **Container Management Tool Paths** section.
3. Enter the full path to the `docker` or `podman` binary.

AxonOps Workbench searches common installation paths automatically on all platforms. Custom paths are only needed if the tool is not found through standard system locations.

!!! tip "Podman on Ubuntu"
    Ubuntu-based Linux distributions may experience compatibility issues with Podman. If you encounter problems, switching to Docker is recommended.

---

## Creating a Local Cluster

To create a new local cluster:

1. From the sidebar, navigate to the **Local Clusters** workspace.
2. Click **Create Local Cluster** to open the creation dialog.

<!-- Screenshot: Create Local Cluster dialog showing version dropdown, node slider, and checkboxes -->

3. Configure the cluster settings:

### Cluster Name (Optional)

Enter a descriptive name for your cluster. If left blank, a unique identifier is generated automatically.

### Apache Cassandra Version

Select the Cassandra version to run from the dropdown:

| Version | Notes |
|---------|-------|
| **5.0** | Default. Latest major release. |
| **4.1** | Current LTS-style release. |
| **4.0** | Previous stable release. |

### Number of Nodes

Use the slider to set how many Cassandra nodes to include in the cluster. The range is **1 to 20 nodes**, with a default of **3**.

Each node runs as a separate container. More nodes require more system resources (CPU, RAM, and disk space).

!!! info "Resource considerations"
    Each Cassandra node is configured with a maximum heap size of 256 MB. A 3-node cluster with AxonOps monitoring typically uses around 2-3 GB of RAM. Plan accordingly for larger clusters.

### AxonOps Monitoring

Check **Install AxonOps within the local cluster** to include full monitoring capabilities. This option is enabled by default. See [With AxonOps Monitoring](#with-axonops-monitoring) below for details on what gets deployed.

### Start Immediately

Check **Run the local cluster once created** to start the cluster automatically after creation. If unchecked, the cluster is created but remains stopped until you start it manually.

4. Click **Create Project** to build the cluster.

AxonOps Workbench generates a Docker Compose configuration, allocates random available ports for Cassandra and monitoring services, and saves the project. If you selected the immediate start option, the containers begin pulling images and starting up.

---

## With AxonOps Monitoring

When you enable the AxonOps monitoring option, the following containers are created alongside your Cassandra nodes:

| Container | Image | Purpose |
|-----------|-------|---------|
| **OpenSearch** | `opensearchproject/opensearch:2.18.0` | Metrics and log storage backend |
| **AxonOps Server** | `registry.axonops.com/.../axon-server:latest` | Metrics collection and processing |
| **AxonOps Dashboard** | `registry.axonops.com/.../axon-dash:latest` | Web-based monitoring dashboard |
| **Cassandra Nodes** | `registry.axonops.com/.../cassandra:<version>` | Cassandra with AxonOps agent built in |

The Cassandra container images include the AxonOps agent pre-installed. Each node is configured to report to the AxonOps Server container automatically.

Once all containers are healthy, the AxonOps Dashboard is accessible through a randomly assigned port on `localhost`. The Workbench displays this port in the cluster details and provides a direct link to open the dashboard in your browser.

!!! note "Without AxonOps Monitoring"
    If you uncheck the AxonOps monitoring option, only the Cassandra node containers are created. The OpenSearch, AxonOps Server, and AxonOps Dashboard containers are omitted from the Docker Compose configuration.

---

## Managing Running Clusters

Local clusters appear in the **Local Clusters** workspace in the sidebar. Each cluster card shows the cluster name, Cassandra version, number of nodes, and current status.

### Starting a Cluster

Click the **Start** button on a stopped cluster. AxonOps Workbench runs `docker compose up -d` (or `podman compose up -d`) in the background. Progress is displayed in a live notification that streams the container runtime output.

After the containers start, Workbench waits for Cassandra to become ready by testing the CQL native transport port. This readiness check retries every 5 seconds for up to 6 minutes.

### Stopping a Cluster

Click the **Stop** button on a running cluster. This runs `docker compose down`, which stops and removes the containers while preserving the data volumes.

### Connecting to a Cluster

Once a cluster is running, click **Connect** to open a CQL console connected to the first Cassandra node. The connection uses the randomly assigned native transport port on `localhost`.

### Viewing the Docker Compose File

Each local cluster has a generated `docker-compose.yml` file stored in the application's data directory under `localclusters/<cluster-id>/`. You can inspect this file to understand the full container configuration, including port mappings, environment variables, and volume mounts.

### Deleting a Cluster

To remove a local cluster, stop it first if it is running, then delete it from the cluster list. Deleting a cluster removes the Docker Compose file and associated project data from disk.

---

## Docker Compose Migration

AxonOps Workbench automatically migrates legacy Docker Compose files to a newer format when starting a cluster. This migration replaces older `sed`-based command configurations with environment variables for the AxonOps Dashboard service.

The migration process:

- Runs automatically when you start a cluster -- no manual action is required.
- Creates a timestamped backup of the original file (e.g., `docker-compose.yml.bak.2025012314`) before making changes.
- Logs the migration status for reference.

If the migration is not needed (the file already uses the current format), no changes are made.

!!! info "Backward compatibility"
    Clusters created with older versions of AxonOps Workbench are migrated transparently. The backup file is preserved so you can review what changed if needed.

---

## Sandbox Limits

By default, AxonOps Workbench allows only **1** local cluster to run simultaneously. This limit helps prevent excessive resource consumption on your development machine.

To change this limit:

1. Open the application **Settings**.
2. Navigate to the **Limits** section.
3. Adjust the **Sandbox** value to the desired maximum number of concurrent running clusters.

If you attempt to start a cluster when the limit is reached, Workbench displays a notification explaining the restriction and directing you to the settings to adjust it.

---

## Troubleshooting

### Docker or Podman Not Found

**Symptoms:** Error message stating that `docker compose` or `podman compose` is not installed or not accessible.

**Solutions:**

- Verify that Docker Desktop or Podman is installed and running.
- For Docker, confirm that `docker compose version` returns a valid result in your terminal.
- For Podman, confirm that `podman compose --version` returns a valid result.
- If the tool is installed in a non-standard location, set the custom path in **Settings > Container Management Tool Paths**.
- On macOS, ensure the Docker or Podman CLI tools are linked to a location on your `PATH` (e.g., `/usr/local/bin`).

### Linux User Not in Docker Group

**Symptoms:** Permission denied errors when starting a local cluster on Linux with Docker.

**Solution:**

```bash
sudo usermod -aG docker $USER
```

Log out and log back in, then restart AxonOps Workbench. This is not required when using Podman.

### Port Conflicts

**Symptoms:** Container fails to start with a "port is already in use" error.

**Solutions:**

- AxonOps Workbench assigns random available ports when creating a cluster. If a port conflict occurs, stop the conflicting service or delete and recreate the local cluster to generate new port assignments.
- Check for other running containers or services that may be occupying the required ports.

### Insufficient Disk Space

**Symptoms:** Container images fail to pull, or containers crash shortly after starting.

**Solutions:**

- Ensure you have at least 2 GB of free disk space for a basic cluster, and more for multi-node clusters with monitoring.
- Run `docker system prune` to reclaim space from unused images, containers, and volumes.
- For Podman, use `podman system prune` to achieve the same result.

### Containers Start But Cassandra Is Not Ready

**Symptoms:** The progress notification shows "Cassandra is not ready yet, recheck again in 5 seconds" and eventually times out after 6 minutes.

**Solutions:**

- Verify that your system has sufficient RAM available. Each Cassandra node requires at least 256 MB of heap space plus overhead.
- Check the Docker/Podman logs for the Cassandra containers to identify startup errors.
- Reduce the number of nodes if your system is resource-constrained.

### Podman Compatibility on Ubuntu

**Symptoms:** Local clusters fail to start or behave unexpectedly when using Podman on Ubuntu-based distributions.

**Solution:** Switch to Docker as the container management tool. Ubuntu-based distributions have known compatibility issues with Podman. You can change the tool in **Settings > Features > Container Management Tool**.
