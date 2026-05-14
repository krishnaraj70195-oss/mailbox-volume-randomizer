#!/usr/bin/env python3
"""
Interactive Mailbox Rotation Skill
Supports static daily volumes and 5-day dynamic rotation for organic patterns
"""
import sys
from mailbox_volume_manager import MailboxVolumeManager
import random


def parse_volume_range(range_str: str) -> tuple:
    """Parse volume range like '1-8' or '70-100' into (min, max)"""
    try:
        parts = range_str.strip().split('-')
        if len(parts) != 2:
            raise ValueError
        min_vol = int(parts[0].strip())
        max_vol = int(parts[1].strip())
        if min_vol < 1 or min_vol > max_vol:
            raise ValueError
        return min_vol, max_vol
    except (ValueError, IndexError):
        return None


def generate_organic_distribution(min_vol, max_vol, mailbox_count, target_volume):
    """Generate organic random distribution targeting volume"""
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


def apply_rotation(manager, domain_mailboxes, volumes, domain, target_volume):
    """Apply rotation and show results"""
    final_total = sum(volumes)

    vol_min = min(volumes)
    vol_max = max(volumes)

    print("\n" + "=" * 60)
    print(f"RANDOMIZED {vol_min}-{vol_max} DISTRIBUTION")
    print("=" * 60)
    print(f"Total: {final_total} emails/day")
    print(f"Mailboxes: {len(domain_mailboxes)}\n")

    dist_counts = {}
    for v in sorted(set(volumes)):
        count = volumes.count(v)
        pct = (count / len(volumes)) * 100
        dist_counts[v] = (count, pct)

    for vol in sorted(dist_counts.keys()):
        count, pct = dist_counts[vol]
        print(f"  {count:2d} mailboxes at {vol} emails/day ({pct:5.1f}%)")

    # Dry run
    print("\n--- DRY RUN ---")
    result_dry = manager.apply_volumes(domain_mailboxes, volumes, dry_run=True)
    print(f"✓ Ready to update {result_dry['successful']} mailboxes")
    print(f"✓ Expected volume: {result_dry['expected_volume']} emails/day")

    # Confirmation
    confirm = input("\n✓ Apply these changes? (yes/no): ").strip().lower()
    if confirm == "yes":
        print("\n--- APPLYING ---")
        result = manager.apply_volumes(domain_mailboxes, volumes, dry_run=False)
        print(f"✓ Updated: {result['successful']}/{result['total']} mailboxes")
        print(f"✓ Total daily volume: {result['expected_volume']} emails")
        if result['failed'] > 0:
            print(f"✗ Failed: {result['failed']}")
            for email, error in result['failed_details'][:3]:
                print(f"  {email}: {error}")
    else:
        print("Cancelled.")


def main():
    # Get API token
    token = "OWE0ZmQwOGYtNzlmOS00Y2IwLThkNzgtNTUyMWRmOGQzNWZkOmZMbEpMbmhtQmtJRw=="

    # Step 1: Get domain
    print("=" * 60)
    print("MAILBOX ROTATION SKILL")
    print("=" * 60)
    domain = input("\n📧 Enter domain name (e.g., amanscaling.com): ").strip()
    if not domain:
        print("❌ Domain required")
        return

    # Step 2: Get volume range (per mailbox)
    while True:
        range_input = input("\n📊 Enter volume range per mailbox (e.g., 1-6, 2-8, 1-4): ").strip()
        volume_range = parse_volume_range(range_input)
        if volume_range:
            min_vol, max_vol = volume_range
            print(f"✓ Range: {min_vol}-{max_vol}")
            break
        print("❌ Invalid range. Use format: 1-6")

    # Step 3: Choose mode
    print("\n📅 Rotation Mode?")
    print("  1. Static (same volume every day)")
    print("  2. 5-Day Dynamic (varies daily, stays within range, looks organic)")

    mode = input("\nChoose (1 or 2): ").strip()

    if mode == "2":
        # 5-Day Dynamic Mode
        while True:
            range_input = input("\n📊 Enter target email range for 5 days (e.g., 70-100): ").strip()
            target_range = parse_volume_range(range_input)
            if target_range:
                min_target, max_target = target_range
                print(f"✓ Range: {min_target}-{max_target} emails/day")
                break
            print("❌ Invalid range. Use format: 70-100")

        # Generate 5-day schedule
        print("\n🎲 Generating 5-day schedule...")
        schedule = []
        for day in range(1, 6):
            daily_target = random.randint(min_target, max_target)
            schedule.append(daily_target)

        print("\n5-DAY DYNAMIC ROTATION SCHEDULE:")
        print("(Different volume & distribution each day)")
        for day, target in enumerate(schedule, 1):
            print(f"  Day {day}: {target} emails/day")

        total_sends = schedule[0]  # Apply first day
    else:
        # Static Mode
        while True:
            try:
                total_sends = int(input("\n🎯 Enter total emails/day target (e.g., 250, 300, 500): ").strip())
                if total_sends < 1:
                    raise ValueError
                print(f"✓ Target: {total_sends} emails/day")
                break
            except ValueError:
                print("❌ Please enter a valid number")

    # Connect to Instantly
    print("\n⏳ Fetching mailboxes...")
    manager = MailboxVolumeManager(token)
    all_mailboxes = manager.get_all_mailboxes()
    domain_mailboxes = manager.filter_by_domain(all_mailboxes, domain)

    if not domain_mailboxes:
        print(f"❌ No mailboxes found for {domain}")
        return

    mailbox_count = len(domain_mailboxes)
    print(f"✓ Found {mailbox_count} mailboxes on {domain}")

    # Generate distribution
    volumes = generate_organic_distribution(min_vol, max_vol, mailbox_count, total_sends)

    # Apply rotation
    apply_rotation(manager, domain_mailboxes, volumes, domain, total_sends)


if __name__ == "__main__":
    main()
