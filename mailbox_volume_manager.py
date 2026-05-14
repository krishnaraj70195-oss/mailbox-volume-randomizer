#!/usr/bin/env python3
"""
Mailbox Volume Manager for Instantly.ai
Manage and randomize daily sending volumes across mailboxes to create natural sending patterns.
"""
import requests
import json
import random
from collections import defaultdict
from typing import List, Dict, Optional
import os


class MailboxVolumeManager:
    def __init__(self, token: str, base_url: str = "https://api.instantly.ai"):
        self.token = token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def get_all_mailboxes(self) -> List[Dict]:
        """Fetch all mailboxes with pagination"""
        all_items = []
        starting_after = None

        while True:
            params = {"limit": 100}
            if starting_after:
                params["starting_after"] = starting_after

            response = requests.get(
                f"{self.base_url}/api/v2/accounts",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])

            all_items.extend(items)

            starting_after = data.get("next_starting_after")
            if not starting_after or len(items) < 100:
                break

        return all_items

    def filter_by_domains(self, mailboxes: List[Dict], domains: List[str]) -> List[Dict]:
        """Filter mailboxes by domain list"""
        return [
            mb for mb in mailboxes
            if any(mb.get("email", "").endswith(f"@{domain}") for domain in domains)
        ]

    def filter_by_domain(self, mailboxes: List[Dict], domain: str) -> List[Dict]:
        """Filter mailboxes for a specific domain"""
        return [mb for mb in mailboxes if mb.get("email", "").endswith(f"@{domain}")]

    def randomize_volumes(
        self,
        mailbox_count: int,
        volume_distribution: Optional[List[int]] = None
    ) -> List[int]:
        """
        Generate randomized volumes for mailboxes.

        Args:
            mailbox_count: Number of mailboxes to generate volumes for
            volume_distribution: List to repeat and randomize. Defaults to [0,0,0,1,1,2,2,3,3,4]

        Returns:
            Shuffled list of volumes
        """
        if volume_distribution is None:
            volume_distribution = [0, 0, 0, 1, 1, 2, 2, 3, 3, 4]

        volumes = []
        while len(volumes) < mailbox_count:
            volumes.extend(volume_distribution)

        volumes = volumes[:mailbox_count]
        random.shuffle(volumes)
        return volumes

    def get_target_distribution(self, target_volume: int, mailbox_count: int) -> List[int]:
        """
        Calculate volume distribution to reach target daily volume.

        Args:
            target_volume: Target daily emails (e.g., 100)
            mailbox_count: Number of mailboxes (e.g., 49)

        Returns:
            List of volumes that sum to approximately target_volume
        """
        if mailbox_count == 49:
            # Optimized for 49 mailboxes targeting ~100 emails
            volumes = []
            volumes.extend([0] * 6)
            volumes.extend([1] * 8)
            volumes.extend([2] * 20)
            volumes.extend([3] * 10)
            volumes.extend([4] * 5)
        else:
            # Generic calculation for other sizes
            # Aim for average of target_volume / mailbox_count
            avg = target_volume / mailbox_count
            volumes = [int(avg) for _ in range(mailbox_count)]

        random.shuffle(volumes)
        return volumes[:mailbox_count]

    def update_mailbox_volume(self, email: str, daily_limit: int) -> tuple:
        """Update daily campaign limit for a mailbox"""
        try:
            response = requests.patch(
                f"{self.base_url}/api/v2/accounts/{requests.utils.quote(email)}",
                headers=self.headers,
                json={"daily_limit": daily_limit}
            )
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, str(e)

    def apply_volumes(
        self,
        mailboxes: List[Dict],
        volumes: List[int],
        dry_run: bool = False
    ) -> Dict:
        """Apply volumes to mailboxes"""
        if len(volumes) != len(mailboxes):
            raise ValueError(f"Volume count ({len(volumes)}) must match mailbox count ({len(mailboxes)})")

        successful = 0
        failed = 0
        failed_details = []

        for i, (mb, volume) in enumerate(zip(mailboxes, volumes)):
            email = mb.get("email")
            current_limit = mb.get("daily_limit", 0)

            if current_limit == volume:
                successful += 1
                continue

            if dry_run:
                successful += 1
                continue

            success, error = self.update_mailbox_volume(email, volume)
            if success:
                successful += 1
            else:
                failed += 1
                failed_details.append((email, error))

        return {
            "successful": successful,
            "failed": failed,
            "total": len(mailboxes),
            "failed_details": failed_details,
            "expected_volume": sum(volumes)
        }

    def get_volume_distribution_stats(self, volumes: List[int]) -> Dict:
        """Get statistics about a volume distribution"""
        counts = defaultdict(int)
        for v in volumes:
            counts[v] += 1

        stats = {
            "total_mailboxes": len(volumes),
            "total_volume": sum(volumes),
            "distribution": dict(sorted(counts.items())),
            "percentages": {}
        }

        for volume, count in counts.items():
            pct = (count / len(volumes)) * 100
            stats["percentages"][volume] = f"{pct:.1f}%"

        return stats

    def batch_update_domains(
        self,
        domains: List[str],
        target_volume: Optional[int] = None,
        randomize: bool = False,
        dry_run: bool = False
    ) -> Dict:
        """
        Update volumes for multiple domains.

        Args:
            domains: List of domains to update
            target_volume: Target daily volume per domain (e.g., 100)
            randomize: Use randomized distribution instead of target
            dry_run: Show what would happen without making changes

        Returns:
            Dictionary with results for each domain
        """
        all_mailboxes = self.get_all_mailboxes()
        results = {}
        grand_total_volume = 0

        for domain in domains:
            domain_mailboxes = self.filter_by_domain(all_mailboxes, domain)

            if not domain_mailboxes:
                results[domain] = {"error": "No mailboxes found"}
                continue

            # Generate volumes
            if randomize:
                volumes = self.randomize_volumes(len(domain_mailboxes))
            else:
                volumes = self.get_target_distribution(
                    target_volume or 100,
                    len(domain_mailboxes)
                )

            # Apply volumes
            result = self.apply_volumes(domain_mailboxes, volumes, dry_run=dry_run)

            # Store stats
            stats = self.get_volume_distribution_stats(volumes)
            result["stats"] = stats

            results[domain] = result
            grand_total_volume += result["expected_volume"]

        # Add summary
        results["summary"] = {
            "domains_processed": len(results) - 1,
            "total_mailboxes": sum(r.get("total", 0) for r in results.values() if isinstance(r, dict) and "total" in r),
            "total_daily_volume": grand_total_volume,
            "dry_run": dry_run
        }

        return results


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage daily sending volumes for Instantly.ai mailboxes"
    )
    parser.add_argument(
        "--token",
        required=True,
        help="Instantly API v2 Bearer token"
    )
    parser.add_argument(
        "--domains",
        required=True,
        help="Comma-separated list of domains (e.g., domain1.com,domain2.com)"
    )
    parser.add_argument(
        "--target-volume",
        type=int,
        default=100,
        help="Target daily volume per domain (default: 100)"
    )
    parser.add_argument(
        "--randomize",
        action="store_true",
        help="Use randomized distribution instead of target volume"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes"
    )

    args = parser.parse_args()

    manager = MailboxVolumeManager(args.token)
    domains = [d.strip() for d in args.domains.split(",")]

    results = manager.batch_update_domains(
        domains=domains,
        target_volume=args.target_volume,
        randomize=args.randomize,
        dry_run=args.dry_run
    )

    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
