#!/bin/bash

# FacilityApps API Test Commands
# Replace YOUR_TOKEN with your actual Bearer token

DOMAIN="https://demouk.facilityapps.com"
TOKEN="YOUR_TOKEN_HERE"

echo "========================================="
echo "TEST 1: One-off Job (Site Only)"
echo "========================================="
curl -X POST "${DOMAIN}/api/1.0/planning/save/true" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
  "id": null,
  "sequence_date": null,
  "editMode": "all",
  "mode": "roster",
  "translations": [{"id": "new-0", "regionCode": "en_EN", "text": "Daily clean - One-off"}],
  "description_translations": [{"id": "new-0", "regionCode": "en_EN", "text": "Single occurrence job"}],
  "date_start": "2025-11-01",
  "date_end": "2025-11-01",
  "hour_start": "9",
  "minute_start": "0",
  "hour_end": "17",
  "minute_end": "0",
  "locations": "834",
  "floors_spaces": {},
  "contracts": [],
  "rate": null,
  "invoicable": false,
  "clock_hourtype_id": null,
  "duration_seconds": null,
  "owners": [{"id": "17"}],
  "owner_roles": [],
  "approvers": [],
  "approver_roles": [],
  "watchers": [],
  "watcher_roles": [],
  "subtasks": [],
  "contractSubtask": null,
  "syncForms": false,
  "labels": ["priority", "ext:ROW001"],
  "instruction-documents": [],
  "remove-instruction-documents": [],
  "repeat_interval_length": 1,
  "use_day_of_week": false,
  "frequency_daily_repeat": [],
  "frequency_weekly_repeat": [],
  "frequency_monthly_repeat": [],
  "frequency_stop_repeat": 0,
  "repeat_interval_period": "daily",
  "task_sampling_select": null,
  "subtask_sampling_select": null,
  "exception-mode": 0,
  "excludeExceptions": "1",
  "task_complete_emails": true,
  "task_canceled_emails": true,
  "save_as_concept": false,
  "task_form_submission_id": null,
  "task_form_submission_visible": false
}' | jq .

echo ""
echo "========================================="
echo "TEST 2: Weekly (Mon & Wed)"
echo "========================================="
curl -X POST "${DOMAIN}/api/1.0/planning/save/true" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
  "id": null,
  "sequence_date": "2025-11-04",
  "editMode": "all",
  "mode": "roster",
  "translations": [{"id": "new-0", "regionCode": "en_EN", "text": "Weekly meeting"}],
  "description_translations": [{"id": "new-0", "regionCode": "en_EN", "text": "Every Monday and Wednesday"}],
  "date_start": "2025-11-04",
  "date_end": "2025-12-31",
  "hour_start": "14",
  "minute_start": "0",
  "hour_end": "15",
  "minute_end": "0",
  "locations": "834",
  "floors_spaces": {"10": []},
  "contracts": [],
  "rate": null,
  "invoicable": false,
  "clock_hourtype_id": null,
  "duration_seconds": null,
  "owners": [{"id": "17"}],
  "owner_roles": [],
  "approvers": [],
  "approver_roles": [],
  "watchers": [],
  "watcher_roles": [],
  "subtasks": [],
  "contractSubtask": null,
  "syncForms": false,
  "labels": ["meeting"],
  "instruction-documents": [],
  "remove-instruction-documents": [],
  "repeat_interval_length": 1,
  "use_day_of_week": false,
  "frequency_daily_repeat": [1, 3],
  "frequency_weekly_repeat": [],
  "frequency_monthly_repeat": [],
  "frequency_stop_repeat": 2,
  "repeat_interval_period": "weekly",
  "end_after_date": "2025-12-31",
  "task_sampling_select": null,
  "subtask_sampling_select": null,
  "exception-mode": 0,
  "excludeExceptions": "1",
  "task_complete_emails": false,
  "task_canceled_emails": false,
  "save_as_concept": false,
  "task_form_submission_id": null,
  "task_form_submission_visible": false
}' | jq .

echo ""
echo "========================================="
echo "TEST 3: Monthly (First Monday)"
echo "========================================="
echo "NOTE: date_start is 2025-11-03 (first Monday in Nov)"
curl -X POST "${DOMAIN}/api/1.0/planning/save/true" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
  "id": null,
  "sequence_date": "2025-11-03",
  "editMode": "all",
  "mode": "roster",
  "translations": [{"id": "new-0", "regionCode": "en_EN", "text": "Monthly inspection"}],
  "description_translations": [{"id": "new-0", "regionCode": "en_EN", "text": "First Monday of each month"}],
  "date_start": "2025-11-03",
  "date_end": "2026-01-31",
  "hour_start": "13",
  "minute_start": "0",
  "hour_end": "16",
  "minute_end": "0",
  "locations": "834",
  "floors_spaces": {},
  "contracts": [],
  "rate": null,
  "invoicable": false,
  "clock_hourtype_id": null,
  "duration_seconds": null,
  "owners": [{"id": "17"}],
  "owner_roles": [],
  "approvers": [],
  "approver_roles": [],
  "watchers": [],
  "watcher_roles": [],
  "subtasks": [],
  "contractSubtask": null,
  "syncForms": false,
  "labels": ["inspection", "monthly"],
  "instruction-documents": [],
  "remove-instruction-documents": [],
  "repeat_interval_length": 1,
  "use_day_of_week": true,
  "frequency_daily_repeat": [],
  "frequency_weekly_repeat": [],
  "frequency_monthly_repeat": [],
  "frequency_stop_repeat": 2,
  "repeat_interval_period": "monthly",
  "end_after_date": "2026-01-31",
  "task_sampling_select": null,
  "subtask_sampling_select": null,
  "exception-mode": 0,
  "excludeExceptions": "1",
  "task_complete_emails": false,
  "task_canceled_emails": false,
  "save_as_concept": false,
  "task_form_submission_id": null,
  "task_form_submission_visible": false
}' | jq .

