---
title: "Results & Export"
description: "View query results, export to CSV or PDF, copy as JSON, and work with BLOB data in AxonOps Workbench."
meta:
  - name: keywords
    content: "query results, export CSV, export PDF, copy JSON, BLOB, binary data, AxonOps Workbench"
---

# Results & Export

AxonOps Workbench displays query results in an interactive, feature-rich table and provides straightforward options for exporting data and working with binary (BLOB) columns. This page covers how to navigate result sets, export data in different formats, and handle BLOB content.

## Viewing Results

### Result Blocks

Every CQL statement you execute produces its own **result block** in the output area below the editor. When you run multiple statements at once, each statement maps to a separate sub-output block within the parent block, keeping results cleanly organized and independently scrollable.

<!-- Screenshot: Multiple result blocks showing separate outputs for each CQL statement -->

Each result block displays:

- **Statement badge** — When a block contains more than one statement, a badge shows the total statement count
- **Statement preview** — For multi-statement executions, each sub-output includes the CQL statement that produced it
- **Action buttons** — Download, copy, and query tracing controls appear alongside each result

### Result Grid

Query results from `SELECT` statements are rendered in an interactive table powered by the Tabulator library. The result grid provides a spreadsheet-like experience with the following capabilities:

- **Column sorting** — Click any column header to sort results in ascending or descending order
- **Column resizing** — Drag column borders to adjust widths; columns resize to fit content by default
- **Column reordering** — Drag and drop column headers to rearrange their order
- **Column filtering** — Each column header includes a search input for filtering rows by value
- **Pagination** — Results are paginated with a configurable page size (default: 50 rows per page). Use the pagination controls at the bottom of the table to navigate between pages
- **Row selection** — Click a row's checkbox to select it. Hold <kbd>Shift</kbd> and click to select a range of rows. Hold <kbd>Ctrl</kbd> and click to toggle individual row selection. Use the header checkbox to select or deselect all visible rows on the current page
- **Cell inspection** — Click on a cell to highlight it. Complex data types such as maps, sets, and user-defined types are displayed with a collapsible JSON viewer

<!-- Screenshot: Result grid showing Tabulator table with column headers, sorting arrows, pagination controls, and row checkboxes -->

### Server-Side Paging

For large result sets, the Workbench fetches data incrementally from the Cassandra cluster rather than loading everything at once. When additional rows are available beyond the current page:

1. A **Next** button appears in the paginator area of the result table
2. Clicking **Next** fetches the next batch of rows from the server and appends them to the table
3. A spinner indicator displays while the next page is being retrieved
4. Once all rows have been fetched, the standard **Last** page button reappears and normal local pagination resumes

This approach keeps the application responsive even when querying tables with large numbers of rows.

### Copying Results

Click the **Copy** button on any result block to copy its contents to the clipboard in JSON format. The copied output includes both the original CQL statement and the result data, formatted as a readable JSON object.

## Exporting Results

Each result block that contains tabular data provides export options accessible through the **Download** button. Click the download icon to reveal the available export formats.

<!-- Screenshot: Download options showing CSV and PDF icons next to a result block -->

### CSV Export

Click the **CSV** icon to export the result table as a comma-separated values file. The exported file is named `statement_block.csv` by default and includes:

- A header row with all column names
- All rows currently loaded in the result table
- Standard CSV formatting compatible with spreadsheet applications such as Excel, Google Sheets, and LibreOffice Calc

CSV export is ideal for further data analysis, reporting, or importing results into other tools.

### PDF Export

Click the **PDF** icon to export the result table as a PDF document. The exported file is named `statement_block.pdf` and includes:

- A title derived from the CQL statement that produced the results
- The full result table rendered in portrait orientation

PDF export is suitable for sharing results as a formatted, printable document.

### Copying as JSON

In addition to file exports, the **Copy** button on the block-level action bar copies the entire block contents to the clipboard as a formatted JSON object. This includes the CQL statement text and all output data, making it convenient for pasting into documentation, issue reports, or other tools that accept JSON.

## Working with BLOBs

AxonOps Workbench provides dedicated support for working with Cassandra `blob` columns, including previewing, importing, and exporting binary data directly from the application.

### BLOB Preview

BLOB preview allows you to inspect the contents of a `blob` field by opening it in your system's default application for the detected file type.

**Enabling BLOB Preview:**

BLOB preview is enabled by default. To toggle it:

1. Open **Settings**
2. Navigate to **Features**
3. Set **Preview BLOB** to `true` (enabled) or `false` (disabled)

When enabled, a **Preview Item** option appears in the context menu for `blob` fields in the data editor. Clicking it triggers the following process:

1. The hex-encoded BLOB value is read from the field
2. The Workbench detects the file type by examining the file signature (magic bytes) of the binary data
3. The binary content is written to a temporary file with the appropriate file extension
4. The file opens in your operating system's default application for that file type

!!! note
    BLOB preview works with file types that have recognizable file signatures, such as images (PNG, JPEG, GIF), audio files, and other common binary formats. Files with `application/*` MIME types (such as generic binary data) are excluded from preview.

!!! info
    BLOB conversion and file detection run in a background process to keep the main application responsive.

### BLOB Import

You can insert binary data into `blob` columns by uploading a file directly from the data editor:

1. When editing a row that contains a `blob` column, click the **Upload Item** button next to the BLOB field
2. A file dialog opens where you can select any file from your filesystem
3. The selected file is read and converted to a hex-encoded string (prefixed with `0x`)
4. The hex value is populated into the input field, ready to be saved with your INSERT or UPDATE statement

**Size Limits:**

BLOB uploads are subject to a configurable size limit to prevent accidental insertion of excessively large binary objects:

- **Default limit:** 1 MB
- **Configuration path:** Settings > Limits > `insertBlobSize`
- **Accepted formats:** The limit value supports human-readable size notation (e.g., `1MB`, `2MB`, `500KB`)

If the selected file exceeds the configured limit, the Workbench displays an error notification showing the file size and the current maximum, and the upload is cancelled.

!!! tip
    If you regularly work with larger binary objects, increase the `insertBlobSize` value in your configuration. Keep in mind that very large BLOBs can impact Cassandra performance and should be used judiciously.

### BLOB Export

To export a BLOB value from a result set to a file on disk:

1. Click the **Preview Item** option in the context menu for the `blob` field
2. The Workbench converts the hex-encoded data back to binary and writes it to a temporary file
3. The file opens in the system's default application, from where you can use "Save As" to store it at a permanent location

This workflow makes it straightforward to extract images, documents, or other binary content stored in Cassandra `blob` columns.

### BLOB Conversion

All BLOB operations -- reading files into hex strings for import, and converting hex strings back to binary for preview and export -- are performed in a **background renderer process**. This design ensures that:

- The main application UI remains responsive during conversion of large binary files
- File I/O operations do not block query execution or other user interactions
- A loading spinner appears on the BLOB field while the conversion is in progress

The conversion pipeline works as follows:

- **Import (file to hex):** The file is read into a byte buffer using Node.js file system APIs, then converted to a hex string using byte-to-hex encoding, prefixed with `0x`
- **Export/Preview (hex to file):** The hex string is decoded back to a byte buffer, written to a temporary file in the system's temp directory with a sanitized filename and the detected file extension, then opened with the system's default handler

!!! warning
    Temporary files created during BLOB preview are stored in your operating system's temp directory. These files are not automatically cleaned up by the Workbench. Periodically review and clear your temp directory if you frequently preview large BLOB values.
