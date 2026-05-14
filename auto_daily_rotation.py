#!/usr/bin/env python3
"""
Auto Daily Rotation Script
Applies next day's rotation at 9 AM Asia/Calcutta time
Tracks progress in rotation_status.json
"""
import sys
import json
import os
from datetime import datetime
import pytz
from mailbox_volume_manager import MailboxVolumeManager
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_schedules():
    """Load domain schedules"""
    with open('domain_rotation_schedules.json', 'r') as f:
        return json.load(f)

def load_or_create_status():
    """Load rotation status or create if doesn't exist"""
    status_file = 'rotation_status.json'
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            return json.load(f)
    else:
        return {
            "last_applied": None,
            "current_day": 0,
            "domains": {}
        }

def save_status(status):
    """Save rotation status"""
    with open('rotation_status.json', 'w') as f:
        json.dump(status, f, indent=2)

def generate_organic_distribution(min_vol, max_vol, mailbox_count, target_volume):
    """Generate organic random distribution"""
    volumes = []
    remaining = target_volume

    for i in range(mailbox_count):
        mailboxes_left = mailbox_count - i
        avg_needed = remaining / mailboxes_left

        min_possible = max(min_vol, int(avg_needed - (max_vol - min_vol) / 2))
        max_possible = min(max_vol, int(avg_needed + (max_vol - min_vol) / 2))

        min_possible = max(min_vol, min(max_possible - 1, min_possible))
        max_possible = max(min_possible, min(max_vol, max_possible))

        volume = random.randint(min_possible, max_possible)
        volumes.append(volume)
        remaining -= volume

    while remaining != 0:
        idx = random.randint(0, len(volumes) - 1)
        if remaining > 0 and volumes[idx] < max_vol:
            volumes[idx] += 1
            remaining -= 1
        elif remaining < 0 and volumes[idx] > min_vol:
            volumes[idx] -= 1
            remaining += 1

    random.shuffle(volumes)
    return volumes

def apply_rotation_for_domain(manager, domain, schedule_info, target_volume, min_vol, max_vol):
    """Apply rotation for a single domain"""
    all_mailboxes = manager.get_all_mailboxes()
    domain_mailboxes = manager.filter_by_domain(all_mailboxes, domain)

    if not domain_mailboxes:
        print(f"❌ {domain}: No mailboxes found")
        return False

    mailbox_count = len(domain_mailboxes)
    volumes = generate_organic_distribution(min_vol, max_vol, mailbox_count, target_volume)
    final_total = sum(volumes)

    result = manager.apply_volumes(domain_mailboxes, volumes, dry_run=False)

    if result['successful'] == result['total']:
        print(f"✓ {domain}: {result['successful']}/{result['total']} mailboxes updated → {final_total} emails/day")
        return True
    else:
        print(f"⚠️  {domain}: {result['successful']}/{result['total']} updated (failed: {result['failed']})")
        return False

def main():
    # Check if it's 9 AM IST
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)

    print(f"\n{'='*60}")
    print(f"AUTO DAILY ROTATION - {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"{'='*60}")

    # Only run at 9 AM (allow 9-9:05 window)
    if now.hour != 9 or now.minute > 5:
        print(f"⏭️  Not 9 AM IST yet. Current time: {now.strftime('%H:%M')}")
        return

    # Load schedules and status
    schedules = load_schedules()
    status = load_or_create_status()

    # Check if already applied today
    today = now.strftime('%Y-%m-%d')
    if status.get('last_applied') == today:
        print(f"✓ Already applied today ({today})")
        return

    # Get token
    token = "OWE0ZmQwOGYtNzlmOS00Y2IwLThkNzgtNTUyMWRmOGQzNWZkOmZMbEpMbmhtQmtJRw=="
    manager = MailboxVolumeManager(token)

    # Current day (0-29)
    current_day = status.get('current_day', 0)
    print(f"\nApplying Day {current_day + 1} schedules...\n")

    # Apply to each domain
    success_count = 0
    for domain, info in schedules.items():
        if domain == 'metadata':
            continue

        if current_day >= len(info['schedule']):
            print(f"⚠️  {domain}: Schedule exhausted (day {current_day} >= {len(info['schedule'])})")
            continue

        target = info['schedule'][current_day]
        min_vol = int(info['range'].split('-')[0])
        max_vol = int(info['range'].split('-')[1])

        if apply_rotation_for_domain(manager, domain, info, target, min_vol, max_vol):
            success_count += 1

    # Update status
    status['last_applied'] = today
    status['current_day'] = (current_day + 1) % 30  # Loop back after 30 days
    status['last_run'] = now.isoformat()
    save_status(status)

    print(f"\n✓ Applied {success_count} domains")
    print(f"Next: Day {status['current_day'] + 1} tomorrow at 9 AM IST")

if __name__ == "__main__":
    main()
