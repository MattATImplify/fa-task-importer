# Recurrence Patterns Guide

## Overview

The FacilityApps Job Importer supports **flexible recurrence patterns** for scheduling recurring jobs. You can create jobs that repeat daily, weekly, monthly, or with custom intervals.

## Quick Reference

| Pattern | `recurrence_type` | `recurrence_end_date` | `recurrence_days` | Example |
|---------|-------------------|----------------------|-------------------|---------|
| One-off | `none` or empty | Not needed | Not used | Single job on Nov 1 |
| Daily | `daily` | Required | Not used | Every day for 30 days |
| Weekdays | `weekdays` | Required | Not used | Mon-Fri only |
| Weekly | `weekly` | Required | Required | Every Mon & Wed |
| Bi-weekly | `biweekly` | Required | Required | Every 2 weeks on Thu |
| Monthly | `monthly` | Required | Not used | 15th of each month |

## Recurrence Types

### 1. None (One-Off)

**Use case:** Job happens once, no repeat

**CSV:**
```csv
title_en,date_start,date_end,recurrence_type
"One-time clean","2025-11-01","2025-11-01",none
```

or simply leave recurrence columns empty:
```csv
title_en,date_start,date_end
"One-time clean","2025-11-01","2025-11-01"
```

**Result:** Job created for Nov 1 only

---

### 2. Daily

**Use case:** Job repeats every day (Mon-Sun) for a period

**CSV:**
```csv
title_en,date_start,recurrence_type,recurrence_end_date
"Daily inspection","2025-11-01",daily,"2025-11-30"
```

**Result:** Job created every day from Nov 1 to Nov 30 (30 occurrences)

**With custom interval:**
```csv
recurrence_type,recurrence_interval,recurrence_end_date
daily,2,"2025-11-30"
```
Repeats every 2 days (odd days: 1st, 3rd, 5th, etc.)

---

### 3. Weekdays

**Use case:** Job repeats Monday to Friday, skips weekends

**CSV:**
```csv
title_en,date_start,recurrence_type,recurrence_end_date
"Weekday cleaning","2025-11-03",weekdays,"2025-11-28"
```

**Result:** Job created Mon-Fri only, no Sat/Sun (approximately 20 occurrences for the month)

**Note:** Weekdays always means Mon-Fri, you cannot customize which days

---

### 4. Weekly

**Use case:** Job repeats on specific days each week

**CSV (Single Day):**
```csv
title_en,date_start,recurrence_type,recurrence_end_date,recurrence_days
"Weekly meeting","2025-11-03",weekly,"2025-12-31","Mon"
```

**CSV (Multiple Days):**
```csv
recurrence_type,recurrence_days
weekly,"Mon,Wed,Fri"
```

**Result:** Job created every Monday, Wednesday, and Friday

**Valid day names:**
- `Mon`, `Tue`, `Wed`, `Thu`, `Fri`, `Sat`, `Sun`
- Case-insensitive: `mon`, `MON`, `Monday` all work
- Comma-separated: `"Mon,Wed,Fri"`

**Default behavior:**
If you don't specify `recurrence_days`, it defaults to the same day of week as `date_start`:
```csv
date_start,recurrence_type,recurrence_end_date,recurrence_days
"2025-11-06",weekly,"2025-12-31",
```
This creates job every Thursday (Nov 6 is a Thursday)

---

### 5. Bi-weekly

**Use case:** Job repeats every 2 weeks on specific days

**CSV:**
```csv
title_en,date_start,recurrence_type,recurrence_end_date,recurrence_days
"Bi-weekly maintenance","2025-11-04",biweekly,"2026-02-28","Tue"
```

**Result:** Job created every other Tuesday

**Multiple days:**
```csv
recurrence_days
"Mon,Thu"
```
Job created every other Monday AND Thursday (same weeks)

**How it works:**
- Week 1: Job occurs on specified days
- Week 2: Skip
- Week 3: Job occurs on specified days
- Week 4: Skip
- Continues this pattern until `recurrence_end_date`

---

### 6. Monthly

**Use case:** Job repeats on the same day of each month

**CSV:**
```csv
title_en,date_start,recurrence_type,recurrence_end_date
"Monthly inspection","2025-11-15",monthly,"2026-11-15"
```

**Result:** Job created on the 15th of every month from Nov 2025 to Nov 2026

**Day selection:** Uses the day from `date_start`
- If `date_start` is Nov 1 → creates jobs on 1st of each month
- If `date_start` is Nov 15 → creates jobs on 15th of each month
- If `date_start` is Nov 30 → creates jobs on 30th (or last day if month has <30 days)

**Custom interval:**
```csv
recurrence_interval
2
```
Repeats every 2 months (Jan, Mar, May, Jul, Sep, Nov)

---

## Advanced Examples

### Example 1: Quarterly Inspections

**Goal:** Inspection on the 1st of every 3 months

```csv
title_en,date_start,recurrence_type,recurrence_interval,recurrence_end_date
"Quarterly inspection","2025-11-01",monthly,3,"2026-11-01"
```

**Result:** Nov 1, Feb 1, May 1, Aug 1, Nov 1

---

### Example 2: Complex Weekly Pattern

**Goal:** Team meetings Mon/Wed/Fri for 6 months

```csv
title_en,date_start,recurrence_type,recurrence_days,recurrence_end_date
"Team standup","2025-11-03",weekly,"Mon,Wed,Fri","2026-05-01"
```

**Result:** ~78 occurrences (26 weeks × 3 days/week)

---

### Example 3: Bi-weekly Deep Clean

**Goal:** Deep clean every other Friday

```csv
title_en,date_start,recurrence_type,recurrence_days,recurrence_end_date
"Deep clean","2025-11-01",biweekly,"Fri","2026-01-31"
```

**Result:** Nov 1, Nov 15, Nov 29, Dec 13, Dec 27, Jan 10, Jan 24

---

## Validation & Error Messages

### Common Errors

**1. Missing End Date**
```
ERROR: recurrence_end_date required for recurring jobs
```
**Fix:** Add `recurrence_end_date` column with date > `date_start`

**2. Invalid Recurrence Type**
```
ERROR: recurrence_type 'weekly-daily' is invalid
```
**Fix:** Use only: `none`, `daily`, `weekdays`, `weekly`, `biweekly`, `monthly`

**3. Invalid Days**
```
ERROR: Invalid day(s): Monday, Weds
```
**Fix:** Use 3-letter abbreviations: `Mon`, `Tue`, `Wed`, `Thu`, `Fri`, `Sat`, `Sun`

**4. End Date Before Start**
```
ERROR: recurrence_end_date 2025-10-31 must be after date_start 2025-11-01
```
**Fix:** Set `recurrence_end_date` > `date_start`

**5. Invalid Interval**
```
ERROR: recurrence_interval must be an integer
```
**Fix:** Use whole numbers: 1, 2, 3, etc.

---

## Tips & Best Practices

### 1. Plan Your End Date

**Consider:**
- Contract duration
- Seasonal work (summer only, winter only)
- Budget cycles
- Review periods

**Example:**
```csv
# 3-month trial period
recurrence_end_date
"2026-02-01"  # Ends after 3 months

# Full year
recurrence_end_date
"2026-11-01"  # Annual contract
```

### 2. Use Weekdays for Business Hours

Most facilities only need cleaning Mon-Fri:
```csv
recurrence_type
weekdays  # Automatic Mon-Fri, no need to specify days
```

### 3. Bi-weekly vs Weekly with Interval

These are the SAME:
```csv
# Option 1: Bi-weekly
recurrence_type,recurrence_days
biweekly,"Thu"

# Option 2: Weekly with interval
recurrence_type,recurrence_days,recurrence_interval
weekly,"Thu",2
```

Use whichever is clearer to you!

### 4. Monthly Edge Cases

Be careful with months that have fewer days:
```csv
# If date_start is Jan 31
date_start,recurrence_type
"2025-01-31",monthly
```

**Result:** 
- Jan 31 ✅
- Feb 28 (31st doesn't exist in Feb)
- Mar 31 ✅
- Apr 30 (31st doesn't exist in Apr)
- May 31 ✅

The system automatically adjusts to the last day of shorter months.

### 5. Testing Recurrence

Start with a short test period:
```csv
# Test for 2 weeks first
recurrence_end_date
"2025-11-15"
```

Then expand once confirmed working:
```csv
# Full deployment
recurrence_end_date
"2026-11-01"
```

---

## Mixing Recurrence Patterns

You CAN have different recurrence types in the same CSV:

```csv
title_en,recurrence_type
"Daily inspection",daily
"Weekly meeting",weekly
"Monthly report",monthly
"One-off audit",none
```

Each row is independent!

---

## FAQ

**Q: Can I have multiple different weekly patterns?**
A: Yes! Use separate rows:
```csv
title_en,recurrence_days
"Morning meetings","Mon,Wed,Fri"
"Planning sessions","Tue,Thu"
```

**Q: How do I stop a recurrence early?**
A: Set `recurrence_end_date` to an earlier date. You'll need to re-import or edit in FA.

**Q: Can I skip specific dates (holidays)?**
A: Not in CSV import. Use FA's exception dates feature after import.

**Q: What happens if recurrence_end_date is far in the future?**
A: FA will create the series. Be careful with distant end dates (performance impact).

**Q: Can I have different times for different days?**
A: No, use separate rows:
```csv
title_en,recurrence_days,hour_start
"AM shift","Mon,Wed,Fri",8
"PM shift","Tue,Thu",14
```

---

**Pro Tip:** Start simple with one-off or daily, then add complexity as you get familiar with the patterns!

