#!/usr/bin/env python3
"""
Interactive Mailbox Rotation Skill
Prompts user for domain, volume range, and total sends, then applies rotation
"""
import sys
from mailbox_volume_manager import MailboxVolumeManager
import random


def parse_volume_range(range_str: str) -> tuple:
    """Parse volume range like '1-8' or '2-6' into (min, max)"""
    try:
        parts = range_str.strip().split('-')
        if len(parts) != 2:
            raise ValueError
        min_vol = int(parts[0].strip())
        max_vol = int(parts[1].strip())
        if min_vol < 1 or max_vol > 10 or min_vol > max_vol:
            raise ValueError
        return min_vol, max_vol
    except (ValueError, IndexError):
        return None


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

    # Step 2: Get volume range
    while True:
        range_input = input("\n📊 Enter volume range (e.g., 1-6, 2-8, 1-4): ").strip()
        volume_range = parse_volume_range(range_input)
        if volume_range:
            min_vol, max_vol = volume_range
            print(f"✓ Range: {min_vol}-{max_vol}")
            break
        print("❌ Invalid range. Use format: 1-6")

    # Step 3: Get total sends target
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

    # Generate organic random distribution (not even patterns)
    volumes = []
    remaining = total_sends

    for i in range(mailbox_count):
        # Calculate min/max for this mailbox to stay within target
        mailboxes_left = mailbox_count - i
        avg_needed = remaining / mailboxes_left

        # Random within range, biased toward average needed
        min_possible = max(min_vol, int(avg_needed - (max_vol - min_vol) / 2))
        max_possible = min(max_vol, int(avg_needed + (max_vol - min_vol) / 2))

        # Clamp to valid range
        min_possible = max(min_vol, min(max_possible - 1, min_possible))
        max_possible = max(min_possible, min(max_vol, max_possible))

        # Random value in range
        volume = random.randint(min_possible, max_possible)
        volumes.append(volume)
        remaining -= volume

    # Fine-tune remaining difference with organic adjustments
    while remaining != 0:
        idx = random.randint(0, len(volumes) - 1)
        if remaining > 0 and volumes[idx] < max_vol:
            volumes[idx] += 1
            remaining -= 1
        elif remaining < 0 and volumes[idx] > min_vol:
            volumes[idx] -= 1
            remaining += 1

    random.shuffle(volumes)
    final_total = sum(volumes)

    # Show distribution
    print("\n" + "=" * 60)
    print(f"RANDOMIZED {min_vol}-{max_vol} DISTRIBUTION")
    print("=" * 60)
    print(f"Total: {final_total} emails/day")
    print(f"Mailboxes: {mailbox_count}\n")

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


if __name__ == "__main__":
    main()
