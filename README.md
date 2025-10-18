# FacilityApps Bulk Job Importer

Local-first Streamlit application for validating and importing one-off jobs/rosters into FacilityApps. This MVP focuses on bulk import validation with comprehensive audit trails and optional direct API posting.

## Features

- ✅ **CSV Validation** – Comprehensive validation against FacilityApps requirements
- 📊 **Audit Reports** – Detailed issue tracking with error/warning/success status
- ✏️ **Inline Editing** – Fix CSV data directly in the UI
- 💾 **Export Results** – Timestamped audit reports and validated CSVs
- 🚀 **Optional Import** – Post validated jobs to FacilityApps (toggle-protected)
- 🔒 **Safe by Default** – Import disabled unless explicitly enabled
- 🌍 **Europe/London Timezone** – All dates validated in UK timezone

## Requirements

- Python 3.10 or higher
- FacilityApps API access (domain + bearer token)

## Installation

1. **Clone or download this repository**

2. **Create a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   Create a `.env` file in the project root:

   ```env
   FA_DOMAIN=demouk.facilityapps.com
   FA_TOKEN=your_bearer_token_here
   ```

   > **Note:** Never commit your `.env` file. Use `.env.example` as a template.

## Usage

1. **Start the application**

   ```bash
   streamlit run app.py
   ```

   The app will open in your browser at `http://localhost:8501`

2. **Configure connection** (Sidebar)
   - Enter your FacilityApps domain (or it will load from `.env`)
   - Enter your bearer token (or it will load from `.env`)
   - Click **"Test Connectivity"** to verify

3. **Load reference data**
   - Click **"Load Sites/Floors/Spaces/Users"**
   - Wait for lookups to load (cached for 5 minutes)
   - Sidebar shows counts: sites, floors, spaces, users

4. **View & Download Lookup Tables** 📚
   - Browse available Sites, Floors, and Spaces in the tabs
   - See which names you can use in your CSV
   - Download lookup CSVs for offline reference
   - Use these names in your import CSV - no IDs needed!

5. **Upload CSV**
   - Click **"Choose CSV file"** and select your jobs CSV
   - Preview the data in the expandable table

6. **Audit & Fix**
   - Click **"Audit & Validate"** to run validation
   - Review issues in the audit table (filter by ERROR/WARN/OK)
   - Edit data in the **"Edit CSV Data"** section if needed
   - Click **"Re-audit"** after making changes
   - Click **"Export Audit & Ready CSVs"** to save results to `./runs/{timestamp}/`

7. **Import (Optional)**
   - Enable **"Enable Import"** toggle in sidebar (⚠️ writes are disabled by default)
   - Click **"Run Import"** to post validated jobs to FacilityApps
   - View success/failure counts and check `./runs/{timestamp}/` for details

## CSV Format

### Required Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `title_en` | string | Job title in English | "Daily clean" |
| `date_start` | date | Start date (YYYY-MM-DD) | "2025-11-01" |
| `date_end` | date | End date (YYYY-MM-DD) | "2025-11-01" |
| `hour_start` | int | Start hour (0-23) | 9 |
| `minute_start` | int | Start minute (0-59) | 0 |
| `hour_end` | int | End hour (0-23) | 17 |
| `minute_end` | int | End minute (0-59) | 0 |

**Location (use names - no IDs needed!):**
- `site_name` (required) - Use the lookup tables to find available names
- `floor_name` (optional) - Must belong to the site
- `space_name` (optional) - Must belong to the floor

**Owner (use email or name):**
- `owner_email` OR `owner_name` (at least one required)

> **💡 Pro Tip:** After loading lookups, download the reference tables (Sites, Floors, Spaces) to see all available names. No need to look up IDs!

### Optional Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `description_en` | string | Job description | "Ground floor bathrooms" |
| `label_list` | string | Comma-separated labels | "priority,ext:ROW001" |

### Recurrence Columns (Optional)

For recurring jobs, add these columns. Leave empty or set `recurrence_type` to `none` for one-off jobs.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `recurrence_type` | string | Pattern type | `daily`, `weekdays`, `weekly`, `biweekly`, `monthly`, or `none` |
| `recurrence_end_date` | date | When to stop recurring (YYYY-MM-DD) | "2025-12-31" |
| `recurrence_days` | string | Days of week (for weekly/biweekly) | "Mon,Wed,Fri" |
| `recurrence_interval` | int | Interval multiplier (optional, default 1) | 1, 2, 3, etc. |

**Recurrence Types:**

- **`none`** (default) - One-off job, occurs once on `date_start`
- **`daily`** - Every day (Mon-Sun) until `recurrence_end_date`
- **`weekdays`** - Monday to Friday only until `recurrence_end_date`
- **`weekly`** - Specific days each week (use `recurrence_days`)
- **`biweekly`** - Every 2 weeks on specific days (use `recurrence_days`)
- **`monthly`** - Same day each month (e.g., 15th of every month)

### Alternative: Using IDs (Legacy)

If you prefer to use IDs instead of names, you can use these columns:
- `site_id` instead of `site_name`
- `floor_id` instead of `floor_name`
- `space_id` instead of `space_name`
- `owner_employee_id` instead of `owner_email`/`owner_name`

**Note:** ID columns are still supported for backward compatibility, but names are recommended for better readability.

### 🆕 Name-Based Lookups

You can now use **names instead of IDs** for sites, floors, spaces, and owners! The app will automatically resolve names to IDs during validation.

**Benefits:**
- ✅ More readable CSVs
- ✅ No need to look up numeric IDs
- ✅ Case-insensitive matching
- ✅ Mix IDs and names in the same file

**How it works:**
1. Provide `site_name` instead of (or alongside) `site_id`
2. Provide `floor_name` instead of `floor_id`
3. Provide `space_name` instead of `space_id`
4. Provide `owner_name` or `owner_email` instead of `owner_employee_id`
5. If both ID and name are provided, ID takes precedence
6. Names are matched case-insensitively

**Examples:**
```csv
# Using IDs (traditional)
site_id,floor_id,space_id,owner_employee_id
828,2,6,13

# Using names (new!)
site_name,floor_name,space_name,owner_email
"Main Building","Ground Floor","Kitchen","john.smith@example.com"

# Mixed approach (IDs + names)
site_id,floor_name,owner_name
828,"Ground Floor","John Smith"
```

### Sample CSV

See `jobs_import_template.csv` with various recurrence examples:

```csv
title_en,recurrence_type,recurrence_end_date,recurrence_days,description
"One-off clean",none,,,"Single occurrence"
"Daily inspection",daily,"2025-11-30",,"Every day"
"Weekday cleaning",weekdays,"2025-11-30",,"Mon-Fri only"
"Weekly meeting",weekly,"2025-12-31","Mon,Wed","Mon & Wed each week"
"Bi-weekly maintenance",biweekly,"2026-02-28","Tue","Every 2 weeks"
"Monthly inspection",monthly,"2026-01-31",,"Same day each month"
```

### Recurrence Examples

**One-Off Job** (no recurrence):
```csv
recurrence_type,recurrence_end_date
none,
```
or just leave columns empty

**Daily (Every Day)**:
```csv
recurrence_type,recurrence_end_date
daily,"2025-12-31"
```
Creates jobs Mon-Sun from `date_start` to `recurrence_end_date`

**Weekdays Only** (Mon-Fri):
```csv
recurrence_type,recurrence_end_date
weekdays,"2025-12-31"
```
Skips weekends automatically

**Weekly** (Specific Days):
```csv
recurrence_type,recurrence_end_date,recurrence_days
weekly,"2025-12-31","Mon,Wed,Fri"
```
Every Monday, Wednesday, and Friday

**Bi-weekly** (Every 2 Weeks):
```csv
recurrence_type,recurrence_end_date,recurrence_days
biweekly,"2026-03-31","Thu"
```
Every other Thursday

**Monthly** (Same Day Each Month):
```csv
recurrence_type,recurrence_end_date
monthly,"2026-12-31"
```
If `date_start` is Nov 15, creates job on 15th of each month until end date

## Validation Rules

### Date & Time Rules

- All dates interpreted in **Europe/London** timezone
- `date_start` must be >= today (no past dates)
- `date_end` must be >= `date_start` (for one-off jobs)
- `end_time` must be > `start_time`

### Recurrence Rules

- **`recurrence_type`** must be one of: `none`, `daily`, `weekdays`, `weekly`, `biweekly`, `monthly`
- **`recurrence_end_date`** is **required** for recurring jobs (must be > `date_start`)
- **`recurrence_days`** format: comma-separated day names (Mon, Tue, Wed, Thu, Fri, Sat, Sun)
  - Required for `weekly` and `biweekly` types (or defaults to start day)
  - Not used for `daily`, `weekdays`, or `monthly` types
- **`recurrence_interval`** must be a positive integer (1, 2, 3, etc.)
  - For `daily`: repeat every N days
  - For `weekly`/`biweekly`: repeat every N weeks
  - For `monthly`: repeat every N months
- One-off jobs: leave `recurrence_type` empty or set to `none` (no end date needed)

### Hierarchy Rules

- `site_id` must exist in FacilityApps sites
- `floor_id` (if provided) must belong to the specified `site_id`
- `space_id` (if provided) must belong to the specified `floor_id`
- `space_id` cannot be used without `floor_id`

### Owner Rules

- `owner_employee_id` must exist in `/api/v1/user` (paginated lookup)

### Label Rules

- Labels are split by comma, trimmed, and deduplicated
- Warnings shown if duplicates detected

### Duplicate Detection

Rows are considered duplicates if they share:
- Same `site_id`, `floor_id`, `space_id`, `title_en`, `date_start`, `hour_start`, `minute_start`

## API Payload Structure

### One-Off Jobs

This MVP creates **one-off jobs** (no recurrence). Each valid row becomes:

```json
{
  "mode": "roster",
  "date_start": "2025-11-01",
  "date_end": "2025-11-01",
  "hour_start": "9",
  "minute_start": "0",
  "hour_end": "17",
  "minute_end": "0",
  "locations": "828",
  "floors_spaces": {},
  "owners": [{"id": "13"}],
  "labels": ["priority", "ext:ROW001"],
  ...
}
```

### `floors_spaces` Logic

| Scenario | `floors_spaces` Value |
|----------|----------------------|
| Site only | `{}` |
| Site + Floor | `{"<floor_id>": []}` |
| Site + Floor + Space | `{"<floor_id>": ["<space_id>"]}` |

## Output Files

All outputs are written to `./runs/{timestamp}/`:

### After Audit Export

- **`audit_report.csv`** – All validation issues (row_number, status, issue_code, detail, suggestion)
- **`validated_ready.csv`** – Rows with no errors (ready for import)
- **`lookup_cache.json`** – Snapshot of sites/floors/spaces at validation time
- **`run_summary.json`** – Metadata (domain, counts, timezone)

### After Import (if enabled)

- **`created_ids.csv`** – Successfully created jobs (row, job_id, title)
- **`failures.csv`** – Failed imports (row, status, error, title)

## API Endpoints Used

### Read Operations

- `GET https://{domain}/api/v1/planning/sites` – Fetch all sites
- `GET https://{domain}/api/v1/planning/floors` – Fetch all floors
- `GET https://{domain}/api/v1/planning/spaces` – Fetch all spaces
- `GET https://{domain}/api/v1/user?limit=200&page={n}` – Fetch users (paginated)

### Write Operations

- `POST https://{domain}/api/1.0/planning/save/true` – Create job/roster

All requests use:
- Header: `Authorization: Bearer <token>`
- Header: `Accept: application/json`

## Rate Limiting & Retries

- Import runs at **~1 request/second** by default
- Respects `X-RateLimit-Remaining` header (backs off if < 5)
- Retries 5xx errors with **exponential backoff** (max 3 attempts)
- Aborts if failure rate exceeds **10%** (configurable)

## Security

- Bearer tokens are **redacted in logs** (shows first/last 4 chars only)
- `.env` file excluded from version control
- Import **disabled by default** – requires explicit toggle

## Troubleshooting

### "Connection error" when testing

- Check your `FA_DOMAIN` format (no `https://` prefix)
- Verify your `FA_TOKEN` is valid and not expired
- Ensure you have network access to the FA domain

### "Invalid site/floor/space" errors

- Make sure you've clicked **"Load Sites/Floors/Spaces/Users"** first
- Verify the IDs in your CSV match the IDs in FacilityApps
- Check that floor belongs to site, space belongs to floor

### "Past date" errors

- Remember: all dates are validated against **Europe/London** timezone
- If you're in a different timezone, account for the difference
- Use dates >= today in London time

### Import failures

- Check `./runs/{timestamp}/failures.csv` for detailed error messages
- Common issues: invalid FK relationships, malformed data
- Try with a smaller batch first to test

## Architecture Notes

### Timezone Handling

All date validation uses `Europe/London` timezone via `pytz`. This ensures:
- "Today" is calculated correctly for UK-based FA instances
- Date comparisons account for BST/GMT transitions

### In-Memory Caching

Lookups (sites/floors/spaces/users) are stored in Streamlit session state. Streamlit's caching is NOT used because we want explicit control over when to refresh.

### Error Handling

- **Row-level errors don't block other rows** – validation continues
- **Import aborts if >10% fail** – prevents mass failures
- **All errors logged to CSV** – for post-mortem analysis

## Limitations (MVP)

- ✅ One-off jobs only (no recurrence)
- ✅ Site-only jobs (no multi-site)
- ✅ Single owner per job
- ✅ No approvers/watchers in CSV (can be added to payload if needed)
- ✅ No form attachments or instructions
- ✅ No fuzzy matching for IDs (exact match required)

## Future Enhancements

- Fuzzy suggestions for closest site/floor/space/user
- Batch find/replace for owners/sites
- Idempotency ledger to detect re-imports
- Support for recurring jobs (weekly, monthly, etc.)
- Multi-site jobs
- Approvers and watchers in CSV

## License

Proprietary – Internal use only

## Support

For issues or questions, contact your FacilityApps administrator.

---

**Version:** 1.0.0-MVP  
**Last Updated:** October 2025

