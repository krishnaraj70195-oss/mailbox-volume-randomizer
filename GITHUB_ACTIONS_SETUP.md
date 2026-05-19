# GitHub Actions Auto-Rotation Setup

**Status**: ✅ LIVE (May 19, 2026)  
**Cost**: FREE (GitHub free tier)  
**Replaces**: Railway scheduler  

## What It Does

Automatically rotates mailbox volumes daily at **9 AM IST** across 5 domains (247 mailboxes, 1,028 emails/day).

## Current Configuration

| Domain | Emails/Day | Mailboxes | Range | Schedule |
|--------|-----------|-----------|-------|----------|
| withamanacqs.com | 163 | 49 | 1-5 | 160-165 daily |
| heyamanacqs.com | 159 | 49 | 1-5 | 159-165 daily |
| amanscaling.com | 160 | 49 | 1-5 | 160-165 daily |
| mysinghacqs.com | 276 | 100 | 1-5 | 270-280 daily |
| thesinghacqs.com | 270 | 100 | 1-5 | 265-275 daily |

## Setup (One-Time)

### 1. Add GitHub Secrets

Go to: **Settings → Secrets and variables → Actions → New repository secret**

Add these 2 secrets:

```
Name: INSTANTLY_API_TOKEN
Value: OWE0ZmQwOGYtNzlmOS00Y2IwLThkNzgtNTUyMWRmOGQzNWZkOmZMbEpMbmhtQmtJRw==
```

```
Name: SLACK_WEBHOOK_URL
Value: <your-slack-webhook-url>
```
(Get this from your Railway project environment variables)

### 2. Test It

Go to: **Actions → Mailbox Daily Rotation → Run workflow → Run workflow**

Should complete in ~30 seconds and send a Slack notification.

### 3. Automatic Schedule

Once secrets are added, the workflow runs **automatically every day at 9 AM IST** (3:30 AM UTC).

## How It Works

1. **Trigger**: Cron job at 3:30 AM UTC (9 AM IST)
2. **Script**: Runs `auto_daily_rotation.py`
3. **Loads**: `domain_rotation_schedules.json` (30-day rotation plan)
4. **Applies**: Next day's target volumes to each domain
5. **Alerts**: Sends Slack notification with results
6. **Saves**: Updates `rotation_status.json` with progress

## Monitoring

**Watch for in Slack:**
- ✅ Success: `Daily rotation complete: 5 domains applied (Day X)`
- ⚠️ Partial: `Rotation with 2 failed domains: ...`
- 🚨 Error: `Rotation Error: [details]`

**Check GitHub Actions:**
- Go to: Actions → Mailbox Daily Rotation
- View latest run logs for details
- Workflow should complete in <1 minute

## Manual Controls

### Trigger Rotation Now
- Go to: Actions → Mailbox Daily Rotation
- Click "Run workflow" button
- Choose "Run workflow"

### Jump to Specific Day
Edit `rotation_status.json`:
```json
{
  "last_applied": "2026-05-19T09:00:00Z",
  "current_day": 10,
  "domains": {}
}
```
Commit & push → Runs next day at target day

### Pause Rotation
Delete `rotation_status.json` file, commit & push
- Workflow still runs but does nothing (status file missing)
- Resume: Recreate `rotation_status.json` with Day 0

### Update Domain Configuration

1. Edit `domain_rotation_schedules.json` (target_range, range, etc.)
2. Regenerate 30-day schedule:
   ```bash
   python3 mailbox_rotation_skill.py
   ```
3. Commit & push
4. Workflow picks up changes on next run

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Workflow fails with "token error" | Check GitHub Secrets are set correctly |
| No Slack notification | Check SLACK_WEBHOOK_URL is correct |
| Volumes not applied | Check `domain_rotation_schedules.json` has domains |
| Old volumes persisting | Check `rotation_status.json` current_day is correct |
| Rotation skipped a day | Check GitHub Actions logs for why workflow didn't run |

## Cost Comparison

| Platform | Cost | Frequency |
|----------|------|-----------|
| Railway (old) | ~$5-10/month | Daily (24/7 service) |
| GitHub Actions (new) | FREE | Daily (minimal compute) |
| **Savings** | **$60-120/year** | — |

## Files

- `.github/workflows/mailbox-rotation.yml` - GitHub Actions workflow
- `auto_daily_rotation.py` - Rotation script
- `domain_rotation_schedules.json` - 30-day rotation plans
- `rotation_status.json` - Daily progress tracker
- `mailbox_volume_manager.py` - API client (Instantly.ai)

## Next Steps

- ✅ Add GitHub Secrets (complete this first)
- ✅ Test manual workflow run
- ✅ Monitor Slack for automated runs
- ⏳ Turn off Railway scheduler (save costs)
- ⏳ Set up backup alerts (optional, Telegram)

## Related Docs

- `CONTRIBUTING.md` - How to contribute changes
- `README.md` - Project overview
- `SKILL.md` - Manual mailbox rotation CLI
