#!/usr/bin/env python3
"""
Example usage of MailboxVolumeManager
"""
from mailbox_volume_manager import MailboxVolumeManager
import json

# Initialize with your token
TOKEN = "YOUR_BASE64_TOKEN_HERE"
manager = MailboxVolumeManager(token=TOKEN)


def example_1_randomize_single_domain():
    """Randomize volumes for a single domain"""
    print("Example 1: Randomize single domain\n")

    results = manager.batch_update_domains(
        domains=["domain1.com"],
        randomize=True,
        dry_run=True  # Use dry_run=False to actually update
    )

    for domain, result in results.items():
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"{domain}:")
            print(f"  Mailboxes: {result['total']}")
            print(f"  Expected daily volume: {result['expected_volume']} emails")
            print(f"  Distribution: {result['stats']['distribution']}")


def example_2_target_multiple_domains():
    """Set target volume for multiple domains"""
    print("\n\nExample 2: Target volume for multiple domains\n")

    results = manager.batch_update_domains(
        domains=["withamanacqs.com", "heyamanacqs.com"],
        target_volume=100,
        randomize=False,
        dry_run=True
    )

    total_volume = 0
    for domain, result in results.items():
        if domain == "summary":
            continue
        if "error" not in result:
            print(f"{domain}:")
            print(f"  Mailboxes: {result['total']}")
            print(f"  Expected volume: {result['expected_volume']} emails/day")
            total_volume += result['expected_volume']

    print(f"\nTotal daily volume across all domains: {total_volume} emails")


def example_3_custom_distribution():
    """Use custom volume distribution"""
    print("\n\nExample 3: Custom distribution\n")

    # Fetch mailboxes
    mailboxes = manager.get_all_mailboxes()
    print(f"Total mailboxes in account: {len(mailboxes)}")

    # Filter by domain
    target = manager.filter_by_domain(mailboxes, "domain.com")
    print(f"Mailboxes in domain.com: {len(target)}")

    # Custom distribution (more conservative)
    custom_dist = [0, 0, 1, 1, 2]  # 40% at 0, 40% at 1, 20% at 2
    volumes = manager.randomize_volumes(len(target), volume_distribution=custom_dist)

    # Check what we'd apply
    stats = manager.get_volume_distribution_stats(volumes)
    print(f"\nExpected distribution:")
    for volume, count in stats['distribution'].items():
        pct = stats['percentages'][volume]
        print(f"  {volume} emails/day: {count} mailboxes ({pct})")

    print(f"Total expected volume: {stats['total_volume']} emails/day")

    # Would apply like this:
    # result = manager.apply_volumes(target, volumes)


def example_4_low_volume_setup():
    """Low volume setup for testing"""
    print("\n\nExample 4: Low volume test setup\n")

    results = manager.batch_update_domains(
        domains=["test-domain.com"],
        target_volume=30,  # Only 30 emails/day
        dry_run=True
    )

    for domain, result in results.items():
        if "error" not in result and domain != "summary":
            print(f"{domain}:")
            print(f"  Expected daily volume: {result['expected_volume']} emails")
            print(f"  Distribution: {result['stats']['distribution']}")


def example_5_programmatic_update():
    """Direct programmatic update"""
    print("\n\nExample 5: Programmatic update\n")

    # Get all mailboxes
    mailboxes = manager.get_all_mailboxes()
    print(f"Found {len(mailboxes)} total mailboxes")

    # Filter to specific domains
    domains_to_update = ["domain1.com", "domain2.com"]
    target_mailboxes = manager.filter_by_domains(mailboxes, domains_to_update)
    print(f"Found {len(target_mailboxes)} in target domains")

    # Generate volumes targeting 100 emails/day
    volumes = manager.get_target_distribution(
        target_volume=100,
        mailbox_count=len(target_mailboxes) // len(domains_to_update)
    )

    # Apply (this would actually update if dry_run=False)
    result = manager.apply_volumes(target_mailboxes, volumes, dry_run=True)

    print(f"\nResults:")
    print(f"  Total mailboxes: {result['total']}")
    print(f"  Expected daily volume: {result['expected_volume']} emails")
    print(f"  Successful updates: {result['successful']}")
    print(f"  Failed updates: {result['failed']}")


if __name__ == "__main__":
    print("=" * 60)
    print("Mailbox Volume Manager Examples")
    print("=" * 60)

    # Run examples (all use dry_run=True, safe to run)
    try:
        example_1_randomize_single_domain()
        example_2_target_multiple_domains()
        example_3_custom_distribution()
        example_4_low_volume_setup()
        example_5_programmatic_update()

        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure to set TOKEN to your actual Instantly API token")
