# Name-Based Lookup Guide

## Overview

The FacilityApps Job Importer now supports **name-based lookups** for sites, floors, spaces, and owners. This means you can use human-readable names in your CSV files instead of numeric IDs!

## Supported Columns

### Sites
- **ID column:** `site_id`
- **Name column:** `site_name`
- **Priority:** If both provided, `site_id` takes precedence

### Floors
- **ID column:** `floor_id`
- **Name column:** `floor_name`
- **Priority:** If both provided, `floor_id` takes precedence
- **Context-aware:** Floor names are matched within the context of their parent site for better accuracy

### Spaces
- **ID column:** `space_id`
- **Name column:** `space_name`
- **Priority:** If both provided, `space_id` takes precedence
- **Context-aware:** Space names are matched within the context of their parent floor

### Owners
- **ID column:** `owner_employee_id`
- **Name column:** `owner_name`
- **Email column:** `owner_email`
- **Priority:** ID → Name → Email (first available is used)

## Matching Rules

1. **Case-Insensitive:** "Main Building", "main building", and "MAIN BUILDING" all match
2. **Whitespace Trimmed:** Leading/trailing spaces are automatically removed
3. **Context-Aware:** Floors are matched within their site, spaces within their floor
4. **Fallback:** If contextual match fails, tries global match (less safe but more flexible)

## CSV Examples

### Example 1: Pure IDs (Traditional)
```csv
title_en,date_start,date_end,hour_start,minute_start,hour_end,minute_end,site_id,floor_id,space_id,owner_employee_id
"Clean bathroom","2025-11-01","2025-11-01",9,0,17,0,828,2,6,13
```

### Example 2: Pure Names (New!)
```csv
title_en,date_start,date_end,hour_start,minute_start,hour_end,minute_end,site_name,floor_name,space_name,owner_email
"Clean bathroom","2025-11-01","2025-11-01",9,0,17,0,"Main Building","Ground Floor","Bathroom A","john.smith@example.com"
```

### Example 3: Mixed Approach
```csv
title_en,date_start,date_end,hour_start,minute_start,hour_end,minute_end,site_id,floor_name,space_name,owner_name
"Clean bathroom","2025-11-01","2025-11-01",9,0,17,0,828,"Ground Floor","Bathroom A","John Smith"
```

### Example 4: Owner by Email
```csv
title_en,date_start,date_end,hour_start,minute_start,hour_end,minute_end,site_name,owner_email
"Site inspection","2025-11-01","2025-11-01",14,0,16,0,"Main Building","inspector@example.com"
```

## How Validation Works

### Step 1: Name Resolution
When you upload a CSV and click "Audit & Validate":

1. App loads all sites/floors/spaces/users from FacilityApps
2. Builds reverse lookup tables (name → ID)
3. For each row, attempts to resolve names to IDs
4. Stores resolved IDs in hidden columns (`_resolved_site_id`, etc.)

### Step 2: Validation
After resolution, the app validates:

1. **Existence:** Does the resolved ID actually exist?
2. **Hierarchy:** Does the floor belong to the site? Does the space belong to the floor?
3. **Dates/Times:** Are they valid and in the correct range?
4. **Duplicates:** Are there duplicate jobs in the file?

### Step 3: Import
When you run import:

1. Uses the **resolved IDs** from validation
2. Builds API payloads with correct numeric IDs
3. Posts to FacilityApps

## Error Messages

### "Site name 'XYZ' not found"
- **Cause:** The site name doesn't match any site in your FacilityApps instance
- **Solution:** Check spelling, check available sites in the "Debug: View Sample Data" section

### "Floor name 'ABC' not found in site 123"
- **Cause:** Floor name doesn't match any floor in the specified site
- **Solution:** Verify the floor exists in that site, check spelling

### "Owner not found by ID, name, or email"
- **Cause:** None of the owner columns matched a user
- **Solution:** Provide valid `owner_employee_id`, `owner_name`, or `owner_email`

### "Floor does not belong to specified site"
- **Cause:** The floor exists but belongs to a different site
- **Solution:** Correct either the site or floor reference

## Best Practices

### ✅ DO:
- Use names for better readability
- Mix IDs and names if some are easier to find
- Use email for owners when names might be ambiguous
- Check the audit report for name resolution issues
- Use the "Debug: View Sample Data" to see what names are available

### ❌ DON'T:
- Rely on abbreviations that might not match exactly
- Assume name matching is fuzzy (it's exact match, case-insensitive only)
- Use special characters that might not match API formatting
- Skip the audit step when using names (always validate first!)

## Troubleshooting

### Names not resolving?

1. **Check the debug section** after loading lookups to see actual names from API
2. **Verify spelling** - must match exactly (case-insensitive)
3. **Check for extra spaces** - though these are trimmed automatically
4. **Try ID instead** - IDs are always more reliable

### Which name field is used?

The app checks these fields in order:
- Sites: `name` → `site_name` → `title`
- Floors: `name` → `floor_name` → `title`
- Spaces: `name` → `space_name` → `title`
- Users: `user_name` → `username` → `name` → `email`

## Technical Details

### Name-to-ID Mapping
- Built once when lookups are loaded
- Stored in session state for fast access
- Case-insensitive dictionary keys (all lowercased)
- Context keys for floors/spaces: `"{parent_id}|{name_lower}"`

### Resolution Priority
1. **ID column** (if present and non-empty) → use directly
2. **Name column** (if present) → lookup in mapping
3. **Email column** (for owners only, if name not found) → lookup in mapping
4. **Error** (if nothing found) → validation error

### Performance
- Name lookups are O(1) dictionary lookups
- No API calls during name resolution (uses cached data)
- Validation performance: ~1000 rows/second

## FAQ

**Q: Can I use both ID and name in the same row?**
A: Yes! ID takes precedence if both are provided.

**Q: Are names case-sensitive?**
A: No, matching is case-insensitive.

**Q: What if two floors have the same name?**
A: The app uses site context to disambiguate. If multiple matches still exist, it picks one (first found).

**Q: Can I use nicknames or abbreviations?**
A: Only if they match exactly what's in FacilityApps. The matching is exact (case-insensitive), not fuzzy.

**Q: Does this work for import?**
A: Yes! The resolved IDs are used when posting to the API.

**Q: Can I see which names are available?**
A: Yes, expand "Debug: View Sample Data" after loading lookups to see actual names.

---

**Version:** 1.1.0  
**Feature Added:** October 2025

