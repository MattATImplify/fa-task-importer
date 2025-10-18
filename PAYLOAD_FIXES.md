# FacilityApps API Payload Fixes

## Summary of Critical Fixes Applied

Based on the official API documentation and analysis of 500 server errors, the following critical fixes have been implemented:

---

## 🔧 Fix #1: Removed `employeeToPosition`

**Problem:** We were sending `employeeToPosition.id` with the same value as the user ID, which is incorrect.

**Before:**
```json
"owners": [{
  "id": "17",
  "employeeToPosition": {
    "id": "17"
  }
}]
```

**After:**
```json
"owners": [{"id": "17"}]
```

**Reason:** We don't have valid position IDs. The API accepts just the user ID.

---

## 🔧 Fix #2: Fixed `frequency_stop_repeat` Logic

**Problem:** When using `frequency_stop_repeat = 2` (stop at date), we were also sending `frequency_stop_repeat_number_value: 10`, which is invalid.

**Rule:**
- `frequency_stop_repeat = 0` (never) → No additional fields
- `frequency_stop_repeat = 1` (after N times) → Include `frequency_stop_repeat_number_value` ONLY
- `frequency_stop_repeat = 2` (stop at date) → Include `end_after_date` ONLY

**Before:**
```json
{
  "frequency_stop_repeat": 2,
  "frequency_stop_repeat_number_value": 10,
  "end_after_date": "2025-11-30"
}
```

**After:**
```json
{
  "frequency_stop_repeat": 2,
  "end_after_date": "2025-11-30"
}
```

---

## 🔧 Fix #3: Fixed Weekly Recurrence (Days of Week)

**Problem:** For weekly patterns (e.g., "Every Monday and Wednesday"), we were using `frequency_weekly_repeat: [1,3]`, but that field is for **week numbers**, not weekdays.

**Before:**
```json
{
  "repeat_interval_period": "weekly",
  "frequency_weekly_repeat": [1, 3]
}
```

**After:**
```json
{
  "repeat_interval_period": "weekly",
  "frequency_daily_repeat": [1, 3]
}
```

**Reason:** According to the API spec:
- `frequency_daily_repeat`: Array of weekdays (1=Mon, 2=Tue, ..., 7=Sun)
- `frequency_weekly_repeat`: Array of week numbers (only used for specific weeks)

---

## 🔧 Fix #4: Fixed Monthly Recurrence ("First Monday each month")

**Problem:** We were setting `frequency_monthly_repeat: [4]` (thinking it was the day of month), but that field is for **month numbers (1-12)**, not days or weekdays.

**Before:**
```json
{
  "repeat_interval_period": "monthly",
  "frequency_monthly_repeat": [4]
}
```

**After:**
```json
{
  "repeat_interval_period": "monthly",
  "use_day_of_week": true
}
```

**Reason:** For "First Monday of each month" patterns:
- Set `use_day_of_week: true`
- The API will automatically repeat on the same weekday and week number as the start date
- Don't set `frequency_monthly_repeat` unless you want specific months only (e.g., [1, 6, 12] for Jan, Jun, Dec)

---

## 🔧 Fix #5: Fixed Email Settings for Recurring Jobs

**Problem:** Recurring jobs (rosters) should have emails OFF by default.

**Before:**
```json
{
  "task_complete_emails": true,
  "task_canceled_emails": true
}
```

**After:**
```json
{
  "task_complete_emails": false,  // for recurring
  "task_canceled_emails": false   // for recurring
}
```

**Rule:**
- One-off jobs: emails ON
- Recurring jobs: emails OFF

---

## 🔧 Fix #6: Set `sequence_date` for Recurring Jobs

**Problem:** `sequence_date` should be set to the start date for recurring jobs, not `null`.

**Before:**
```json
{
  "sequence_date": null
}
```

**After:**
```json
{
  "sequence_date": "2025-11-01"  // for recurring jobs
}
```

---

## 📋 Correct Payload Examples

### One-off Job (Site Only)
```json
{
  "id": null,
  "sequence_date": null,
  "editMode": "all",
  "mode": "roster",
  "date_start": "2025-11-01",
  "date_end": "2025-11-01",
  "locations": "834",
  "floors_spaces": {},
  "owners": [{"id": "17"}],
  "repeat_interval_length": 1,
  "use_day_of_week": false,
  "frequency_daily_repeat": [],
  "frequency_weekly_repeat": [],
  "frequency_monthly_repeat": [],
  "frequency_stop_repeat": 0,
  "repeat_interval_period": "daily",
  "task_complete_emails": true,
  "task_canceled_emails": true
}
```

### Weekdays (Mon-Fri) Daily Repeat
```json
{
  "sequence_date": "2025-11-01",
  "date_start": "2025-11-01",
  "date_end": "2025-11-30",
  "locations": "834",
  "floors_spaces": {"10": []},
  "owners": [{"id": "17"}],
  "repeat_interval_length": 1,
  "repeat_interval_period": "daily",
  "use_day_of_week": false,
  "frequency_daily_repeat": [1, 2, 3, 4, 5],
  "frequency_stop_repeat": 2,
  "end_after_date": "2025-11-30",
  "task_complete_emails": false,
  "task_canceled_emails": false
}
```

### Weekly (Mon & Wed)
```json
{
  "sequence_date": "2025-11-04",
  "date_start": "2025-11-04",
  "date_end": "2025-12-31",
  "repeat_interval_length": 1,
  "repeat_interval_period": "weekly",
  "frequency_daily_repeat": [1, 3],
  "frequency_stop_repeat": 2,
  "end_after_date": "2025-12-31",
  "task_complete_emails": false,
  "task_canceled_emails": false
}
```

### Bi-weekly (Tuesday)
```json
{
  "sequence_date": "2025-11-05",
  "repeat_interval_length": 2,
  "repeat_interval_period": "weekly",
  "frequency_daily_repeat": [2],
  "frequency_stop_repeat": 2,
  "end_after_date": "2026-02-28"
}
```

### Monthly (First Monday each month)
```json
{
  "sequence_date": "2025-11-04",
  "repeat_interval_length": 1,
  "repeat_interval_period": "monthly",
  "use_day_of_week": true,
  "frequency_stop_repeat": 2,
  "end_after_date": "2026-01-31"
}
```

---

## ✅ Validation Checklist

Before sending each payload, the app now validates:

- [ ] `frequency_stop_repeat = 2` → Must have `end_after_date`, NOT `frequency_stop_repeat_number_value`
- [ ] `frequency_stop_repeat = 1` → Must have `frequency_stop_repeat_number_value`, NOT `end_after_date`
- [ ] Weekly patterns → Use `frequency_daily_repeat` for weekdays, NOT `frequency_weekly_repeat`
- [ ] Monthly with day of week → Set `use_day_of_week: true`, NOT `frequency_monthly_repeat`
- [ ] Recurring jobs → `sequence_date` set, emails OFF
- [ ] One-off jobs → `sequence_date: null`, emails ON
- [ ] Owners → Just `{"id": "..."}`, no `employeeToPosition` unless we have valid position IDs

---

## 🎯 Expected Result

With these fixes, the API should now accept all payloads without 500 errors. The payload structure exactly matches the official FacilityApps API documentation.

