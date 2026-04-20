---
title: "DataStax Astra DB Connections"
description: "Connect AxonOps Workbench to DataStax Astra DB using secure connect bundles and application tokens."
meta:
  - name: keywords
    content: "Astra DB, DataStax, cloud Cassandra, secure connect bundle, SCB, AxonOps Workbench"
---

# DataStax Astra DB Connections

DataStax Astra DB is a fully managed Cassandra-as-a-Service platform that eliminates the operational overhead of running Apache Cassandra yourself. AxonOps Workbench connects to Astra DB through a **Secure Connect Bundle (SCB)** and an **application token**, giving you the same CQL Console, schema browsing, and query tracing experience you get with self-hosted clusters.

---

## Prerequisites

Before creating an Astra DB connection in AxonOps Workbench, you need two items from the [Astra DB console](https://astra.datastax.com/){:target="_blank"}:

### Secure Connect Bundle (SCB)

The Secure Connect Bundle is a ZIP file that contains the TLS certificates and connection metadata required to establish an encrypted connection to your Astra DB database.

To download the bundle:

1. Sign in to the [Astra DB console](https://astra.datastax.com/){:target="_blank"}.
2. Select your database.
3. Click **Connect**.
4. Under **Connect using a driver**, download the **Secure Connect Bundle** ZIP file.
5. Save the file to a location on your local machine that you can easily find later.

!!! warning
    Do not extract the ZIP file. AxonOps Workbench expects the bundle as a single `.zip` archive.

### Application Token (Client ID and Client Secret)

An application token provides the credentials that authenticate your connection. Each token includes a **Client ID** and a **Client Secret**.

To generate a token:

1. In the Astra DB console, navigate to **Settings** and then **Token Management** (or select **Tokens** from the Organization settings).
2. Select an appropriate role (for example, **Database Administrator** for full access).
3. Click **Generate Token**.
4. Copy the **Client ID** and **Client Secret** and store them securely. The Client Secret is only displayed once.

!!! tip
    If you need read-only access for exploration purposes, generate a token with the **Database Administrator** or a custom role scoped to your target keyspace.

---

## Connecting to Astra DB

Follow these steps to create a new Astra DB connection in AxonOps Workbench:

1. Open AxonOps Workbench and select a workspace.
2. Click the **Add Connection** button.
3. In the connection dialog, select **DataStax AstraDB** as the connection type. The dialog switches to the Astra DB form.

    <!-- Screenshot: Connection type selector showing "Apache Cassandra" and "DataStax AstraDB" options -->

4. Fill in the connection fields:

    | Field | Description |
    | --- | --- |
    | **Connection Name** | A descriptive label for this connection (e.g., `Production - Astra DB`). |
    | **Username (Client ID)** | The Client ID from your Astra DB application token. |
    | **Password (Client Secret)** | The Client Secret from your Astra DB application token. |
    | **Secure Connection Bundle** | The path to your downloaded SCB ZIP file. Click the field to open a file browser, or drag and drop the ZIP file onto it. |

    <!-- Screenshot: Astra DB connection form with all four fields filled in -->

5. Click **Test Connection** to verify that the Workbench can authenticate and reach your Astra DB database. A successful test confirms that the bundle, Client ID, and Client Secret are all correct.
6. Once the test passes, click **Save** to store the connection.

!!! note
    All four fields are required. If any field is left empty, the test connection button will highlight the missing fields and display an error message.

---

## Editing an Existing Connection

To modify an Astra DB connection after it has been saved:

1. Right-click on the connection in the sidebar and select **Edit**.
2. The connection dialog opens with the existing values pre-filled, including the path to the Secure Connect Bundle.
3. Update any fields as needed -- for example, to point to a new SCB file after rotating your database credentials.
4. Click **Test Connection** to verify the updated settings, then click **Save**.

---

## Credential Security

Astra DB credentials are protected using the same security mechanisms as standard Cassandra connections:

- **OS Keychain Storage** -- Your Client ID and Client Secret are stored in the operating system's native credential manager (macOS Keychain, Windows Credential Manager, or Linux libsecret). They are never written to plain-text configuration files on disk.
- **Per-Installation RSA Encryption** -- Each Workbench installation generates a unique RSA key pair. Credentials are encrypted with this key before being passed to the connection layer, providing an additional layer of protection at rest.

The Secure Connect Bundle path is stored in the connection's metadata, but the bundle itself remains at its original location on your file system. AxonOps Workbench reads the bundle at connection time and does not copy or modify it.

---

## Working with Astra DB

Once connected, Astra DB databases behave like any other Cassandra connection within AxonOps Workbench. The following features are fully supported:

- **CQL Console** -- Write and execute CQL statements with syntax highlighting and auto-completion.
- **Schema Browser** -- Navigate keyspaces, tables, columns, indexes, materialized views, and user-defined types.
- **Query Execution** -- Run SELECT, INSERT, UPDATE, and DELETE statements against your Astra DB tables.
- **Query Tracing** -- Enable tracing on individual queries to analyze execution performance and identify bottlenecks.
- **Result Export** -- Export query results to CSV, JSON, or other supported formats.
- **Schema Snapshots** -- Save and compare point-in-time snapshots of your database schema.
- **CQL Descriptions** -- Generate DDL statements for keyspaces and tables.

!!! info
    Astra DB connections do not display a host and port in the connection list because the endpoint information is embedded within the Secure Connect Bundle.

---

## Limitations

Astra DB is a managed service, and DataStax enforces certain restrictions at the platform level. These are not limitations of AxonOps Workbench itself, but they affect what operations you can perform through the Workbench:

- **DDL Restrictions** -- Some schema operations (such as creating or dropping keyspaces) may be restricted depending on your Astra DB plan and permissions. Table-level DDL (CREATE TABLE, ALTER TABLE, DROP TABLE) is generally available within your assigned keyspaces.
- **No SSH Tunneling** -- Astra DB connections use the Secure Connect Bundle for encrypted transport. The SSH Tunnel tab in the connection dialog does not apply to Astra DB connections.
- **No Custom SSL Configuration** -- TLS encryption is handled entirely by the Secure Connect Bundle. There is no need (or ability) to configure separate CA certificates or client certificates for Astra DB connections.
- **Serverless Availability** -- Astra DB serverless databases may pause after a period of inactivity. If your database is paused, you may need to resume it from the Astra DB console before connecting.
- **Permission-Dependent Features** -- The features available to you depend on the role assigned to your application token. A token with limited permissions may not be able to perform certain schema or data operations.

---

## Troubleshooting

| Symptom | Possible Cause | Resolution |
| --- | --- | --- |
| Connection test fails immediately | Missing or incorrect Client ID / Client Secret | Verify your token credentials in the Astra DB console. Regenerate the token if the Client Secret was lost. |
| Connection test fails with a TLS error | Corrupted or extracted SCB file | Re-download the Secure Connect Bundle from the Astra DB console. Ensure the file is a `.zip` archive and has not been unzipped. |
| Connection test times out | Database is paused or network restrictions | Check the Astra DB console to confirm your database is active. Verify that outbound HTTPS traffic is allowed from your workstation. |
| Schema operations return permission errors | Insufficient token role | Generate a new application token with the appropriate role (e.g., **Database Administrator**) for the operations you need to perform. |
| "All fields are required" error | One or more form fields are empty | Ensure that Connection Name, Client ID, Client Secret, and the SCB file path are all provided. |
