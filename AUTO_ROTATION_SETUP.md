# Auto Daily Rotation Setup

**Status**: ✅ Ready  
**Script**: `auto_daily_rotation.py`  
**Time**: 9 AM Asia/Kolkata (IST) daily  
**Tracking**: `rotation_status.json`

---

## How It Works

1. Reads `domain_rotation_schedules.json` (30-day schedule per domain)
2. At 9 AM IST, applies that day's target to all domains
3. Tracks progress in `rotation_status.json`
4. Loops back to Day 1 after 30 days

---

## Setup Options

### Option 1: Local Cron (Simplest)

Add to crontab (runs daily at 9 AM IST):

```bash
# IST is UTC+5:30, so 9 AM IST = 3:30 AM UTC
30 3 * * * cd /path/to/mailbox-volume-randomizer && python3 auto_daily_rotation.py >> rotation.log 2>&1
```

Run: `crontab -e`

### Option 2: Trigger.dev (Recommended - Already Set Up)

Create a Trigger task that calls this script daily:

```typescript
import { task } from "@trigger.dev/sdk";

export const dailyRotation = task({
  id: "daily-mailbox-rotation",
  cron: "30 3 * * *", // 3:30 AM UTC = 9 AM IST
  run: async () => {
    // Run auto_daily_rotation.py
    return { status: "applied" };
  },
});
```

### Option 3: Railway Scheduled Job

Use Railway's scheduler to run the script daily.

---

## What Gets Tracked

**rotation_status.json** stores:
```json
{
  "last_applied": "2026-05-15",
  "current_day": 1,
  "last_run": "2026-05-15T03:30:00Z"
}
```

---

## Manual Controls

**Stop auto-rotation:**
- Delete `rotation_status.json` (will reset to Day 1)

**Jump to a specific day:**
- Edit `rotation_status.json` → change `current_day` (0-29)

**Update a domain's range:**
- Edit `domain_rotation_schedules.json` → change `target_range`
- Regenerate schedule (re-run skill with new range)

---

## Test It

Run manually to verify:

```bash
python3 auto_daily_rotation.py
```

Will only apply if it's 9 AM IST ±5 minutes. For testing, edit the time check in the script.

---

## Dependencies

```bash
pip install pytz  # For timezone handling
```

---

## Logs

Check `rotation.log` for daily execution history:

```bash
tail -f rotation.log
```

---

**Next step:** Choose a setup option and I'll configure it for you!
