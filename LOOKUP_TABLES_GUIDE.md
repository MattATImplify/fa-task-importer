# Lookup Tables Guide

## Overview

The app now provides **downloadable lookup tables** showing all available sites, floors, and spaces with their names. No more hunting for IDs!

## How to Use

### Step 1: Load Lookups
1. Open the app
2. Click **"Load Sites/Floors/Spaces/Users"**
3. Wait for data to load from FacilityApps

### Step 2: View Available Names
After loading, you'll see a new section: **📚 Available Sites, Floors & Spaces**

This section has three tabs:

#### 📍 Sites Tab
Shows all available sites with columns:
- `site_name` - The name you'll use in your CSV
- `site_id` - The internal ID (for reference only)

#### 🏢 Floors Tab
Shows all floors with columns:
- `site_name` - Which site this floor belongs to
- `floor_name` - The name you'll use in your CSV
- `site_id` - Internal site ID (reference)
- `floor_id` - Internal floor ID (reference)

#### 🚪 Spaces Tab
Shows all spaces with columns:
- `site_name` - Which site this space belongs to
- `floor_name` - Which floor this space is on
- `space_name` - The name you'll use in your CSV
- `floor_id` - Internal floor ID (reference)
- `space_id` - Internal space ID (reference)

### Step 3: Download for Reference
Each tab has a **📥 Download** button to save the lookup table as CSV:
- `sites_lookup.csv`
- `floors_lookup.csv`
- `spaces_lookup.csv`

Keep these files open while building your import CSV!

## Building Your CSV

### Example Workflow

1. **Download the lookup tables**
   ```
   sites_lookup.csv
   floors_lookup.csv
   spaces_lookup.csv
   ```

2. **Open sites_lookup.csv**
   ```csv
   site_name,site_id
   "Main Building",828
   "Warehouse A",829
   "Office Tower",830
   ```

3. **Use the names in your import CSV**
   ```csv
   title_en,site_name,floor_name,space_name,owner_email
   "Clean kitchen","Main Building","Ground Floor","Kitchen","john@example.com"
   ```

### What You Can Do

✅ **Use names only - no IDs needed**
```csv
site_name,floor_name,space_name
"Main Building","Ground Floor","Kitchen"
```

✅ **Site-only jobs**
```csv
site_name,floor_name,space_name
"Main Building",,
```

✅ **Site + Floor (no space)**
```csv
site_name,floor_name,space_name
"Main Building","Ground Floor",
```

✅ **Full hierarchy**
```csv
site_name,floor_name,space_name
"Main Building","Ground Floor","Kitchen"
```

### What You CANNOT Do

❌ **Space without floor**
```csv
site_name,floor_name,space_name
"Main Building",,"Kitchen"  ❌ ERROR: Must provide floor when using space
```

❌ **Floor from different site**
```csv
site_name,floor_name
"Main Building","Warehouse Floor"  ❌ ERROR: Floor doesn't belong to this site
```

## Tips & Tricks

### 1. Copy-Paste Names
Open the lookup CSV in Excel/Google Sheets and copy names directly into your import CSV. Avoids typos!

### 2. Filter by Site
If you're only working with one site, filter the floors/spaces lookup tables:
```
Floors CSV → Filter site_name = "Main Building"
Spaces CSV → Filter site_name = "Main Building"
```

### 3. Case Doesn't Matter
All matching is case-insensitive:
- "Main Building" = "main building" = "MAIN BUILDING" ✅

### 4. Spaces are Trimmed
Leading/trailing spaces are automatically removed:
- " Main Building " → "Main Building" ✅

### 5. Exact Match Required
Names must match exactly (after case/space normalization):
- "Main Bldg" ≠ "Main Building" ❌
- "Main Building" = "Main Building" ✅

## Troubleshooting

### "Site name 'X' not found"
**Cause:** Name doesn't exist or has typo

**Fix:**
1. Check `sites_lookup.csv` for correct spelling
2. Verify case-insensitive match
3. Look for special characters (é, ñ, etc.)

### "Floor name 'Y' not found in site Z"
**Cause:** Floor doesn't belong to that site, or name is wrong

**Fix:**
1. Open `floors_lookup.csv`
2. Filter by `site_name` to see available floors
3. Check spelling matches exactly

### Lookup tables are empty
**Cause:** API didn't return data or returned unexpected format

**Fix:**
1. Expand **"Debug: View Sample Data"** after loading
2. Check if data was received from API
3. Verify token has correct permissions
4. Contact FA support if issue persists

## Advanced: Understanding the Hierarchy

FacilityApps uses a strict 3-level hierarchy:

```
Site (Level 1 - Required)
└── Floor (Level 2 - Optional)
    └── Space (Level 3 - Optional)
```

### Rules
1. **Every job must have a Site**
2. **Floors belong to Sites** (one-to-one)
3. **Spaces belong to Floors** (one-to-one)
4. You can skip levels: Site → Space is NOT allowed (must go Site → Floor → Space)

### Examples

✅ **Valid Hierarchies:**
```
Site only:           Main Building
Site + Floor:        Main Building → Ground Floor
Site + Floor + Space: Main Building → Ground Floor → Kitchen
```

❌ **Invalid Hierarchies:**
```
Site + Space only:    Main Building → Kitchen (missing floor)
Floor only:           Ground Floor (missing site)
Space only:           Kitchen (missing site and floor)
```

## Refresh Lookups

Lookup data is cached in the session. To refresh:

1. **Manual Refresh:** Click **"Load Sites/Floors/Spaces/Users"** again
2. **Automatic:** Restart the app (closes session, clears cache)

**When to refresh:**
- After adding new sites/floors/spaces in FacilityApps
- After renaming locations in FacilityApps
- If lookup tables seem outdated

## Export vs Download

### Download Lookups (Reference Tables)
- **Purpose:** See what names are available
- **Format:** CSV with name + ID columns
- **Use:** Keep open while building import CSV

### Export Audit Results
- **Purpose:** Save validation results
- **Format:** CSV with validation issues
- **Use:** Review errors, share with team

Don't confuse the two!

---

**Pro Tip:** Save the lookup CSVs in your project folder and reference them whenever you're building import files. They're your "dictionary" for what names to use!

