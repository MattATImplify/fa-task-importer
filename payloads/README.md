# Import Payloads Directory

This directory contains JSON payload files that are automatically saved every time a job is imported through the FacilityApps Task Importer.

## File Naming Convention

Files are named using the following pattern:
```
payload_{timestamp}_{session_id}_{job_title}.json
```

Where:
- `timestamp`: YYYYMMDD_HHMMSS format
- `session_id`: Short unique identifier for the import session
- `job_title`: Sanitized job title (max 30 characters)

Example: `payload_20251025_210026_eaca2f81_Test_Job.json`

## File Structure

Each payload file contains:

```json
{
  "metadata": {
    "timestamp": "2025-10-25T21:00:26.633328",
    "session_id": "eaca2f81",
    "job_title": "Test Job",
    "status": "success|failed|attempted",
    "error_message": "Error details if failed",
    "job_data": {
      "title_en": "Test Job",
      "site": "Main Office",
      "floor": "Ground Floor",
      "space": "Reception",
      "assigned_to": "test@example.com",
      "date_start": "2025-01-01"
    }
  },
  "api_payload": {
    "id": null,
    "sequence_date": null,
    "editMode": "all",
    "mode": "roster",
    "translations": [...],
    "date_start": "2025-01-01",
    "locations": "828",
    "floors_spaces": {"2": ["6"]},
    "owners": [...]
  }
}
```

## Status Values

- `attempted`: Payload was built and saved before API call
- `success`: Job was successfully imported to the API
- `failed`: Job import failed (check error_message for details)

## Use Cases

1. **Debugging**: Review exact payloads sent to the API
2. **Auditing**: Track what data was imported and when
3. **Reproduction**: Recreate failed imports with exact same data
4. **Analysis**: Understand payload structure and patterns
5. **Backup**: Keep records of all import attempts

## Management

- Files are automatically created during imports
- No automatic cleanup (files persist indefinitely)
- Use the "Download All Payloads as ZIP" button in the app to export
- Files can be safely deleted if no longer needed

## File Size

Typical payload files are 1-5 KB each, depending on:
- Job title length
- Number of translations
- Complexity of recurrence settings
- Number of owners/approvers

## Security Note

These files contain the exact data sent to the API, including:
- Job details and descriptions
- User assignments
- Location information
- Timing and recurrence data

Ensure appropriate access controls are in place for this directory.
