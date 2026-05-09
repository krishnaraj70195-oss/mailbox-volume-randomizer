# Mailbox Volume Randomizer Skill

**Status**: ✅ Production Ready  
**Purpose**: Randomize or set specific daily sending volumes on Instantly.ai mailboxes  
**Tested**: May 9, 2026 (98 mailboxes across 2 domains)

---

## What This Does

Manages daily sending volumes across mailboxes to create natural sending patterns. Choose between:
- **Randomize**: Vary volumes 0-4 to look organic
- **Target**: Set specific per-domain daily volume (e.g., 100 emails/day per domain)

---

## Quick Start

### Randomize Volumes (Natural Pattern)

```bash
python mailbox_volume_manager.py \
  --token "YOUR_BASE64_TOKEN" \
  --domains "domain1.com,domain2.com" \
  --randomize
```

### Set Target Daily Volume

```bash
python mailbox_volume_manager.py \
  --token "YOUR_BASE64_TOKEN" \
  --domains "domain1.com,domain2.com" \
  --target-volume 100
```

### Dry Run (Preview Changes)

```bash
python mailbox_volume_manager.py \
  --token "YOUR_BASE64_TOKEN" \
  --domains "domain1.com,domain2.com" \
  --target-volume 100 \
  --dry-run
```

---

## Installation

### Step 1: Get API Token

1. Go to Instantly → Settings → API Keys
2. Create v2 token (full base64 string, NOT decoded)
3. Save to `~/.instantly_keys.json`:

```json
{
  "honza": {
    "token": "MjQwMmVl...base64..."
  },
  "main": {
    "token": "OWE0Zm...base64..."
  }
}
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Make Executable

```bash
chmod +x mailbox_volume_manager.py
```

---

## Usage Modes

### Mode 1: Randomized Distribution (0-4 range)

Creates natural variation with fewer mailboxes at max:
- 30% at 0 (don't send)
- 20% at 1 email/day
- 20% at 2 emails/day
- 20% at 3 emails/day
- 10% at 4 emails/day (max)

**Use when:** You want organic-looking sending patterns

```bash
python mailbox_volume_manager.py \
  --token "$(cat ~/.instantly_keys.json | jq -r .main.token)" \
  --domains "withamanacqs.com,heyamanacqs.com" \
  --randomize
```

### Mode 2: Target Volume (Specific Daily Total)

Distributes volumes to hit target daily email count per domain.

**For 49 mailboxes targeting 100 emails/day:**
- 6 at 0 = 0 emails
- 8 at 1 = 8 emails
- 20 at 2 = 40 emails
- 10 at 3 = 30 emails
- 5 at 4 = 20 emails
- **Total: 98 emails/day**

**Use when:** You need predictable daily sending volume

```bash
python mailbox_volume_manager.py \
  --token "YOUR_TOKEN" \
  --domains "withamanacqs.com,heyamanacqs.com" \
  --target-volume 100
```

---

## Python API

```python
from mailbox_volume_manager import MailboxVolumeManager

manager = MailboxVolumeManager(token="YOUR_TOKEN")

# Fetch all mailboxes
mailboxes = manager.get_all_mailboxes()

# Filter by domains
target = manager.filter_by_domains(mailboxes, ["domain1.com", "domain2.com"])

# Generate volumes
volumes = manager.randomize_volumes(len(target))
# OR
volumes = manager.get_target_distribution(target_volume=100, mailbox_count=49)

# Apply to mailboxes
results = manager.apply_volumes(target, volumes)
print(f"Updated: {results['successful']}/{results['total']}")
```

---

## API Reference

### MailboxVolumeManager Class

#### Methods

| Method | Description |
|--------|-------------|
| `get_all_mailboxes()` | Fetch all mailboxes with pagination |
| `filter_by_domains(mailboxes, domains)` | Filter by multiple domains |
| `filter_by_domain(mailboxes, domain)` | Filter by single domain |
| `randomize_volumes(count, distribution)` | Generate randomized volumes |
| `get_target_distribution(target, count)` | Generate volumes for target total |
| `update_mailbox_volume(email, limit)` | Update single mailbox |
| `apply_volumes(mailboxes, volumes, dry_run)` | Apply volumes to batch |
| `batch_update_domains(domains, target_volume, randomize, dry_run)` | Update multiple domains |

---

## Examples

### Example 1: Two domains, 100 emails each, 200 total

```bash
python mailbox_volume_manager.py \
  --token "$(cat ~/.instantly_keys.json | jq -r .main.token)" \
  --domains "withamanacqs.com,heyamanacqs.com" \
  --target-volume 100
```

**Result:**
```
withamanacqs.com: 98 emails/day
heyamanacqs.com: 98 emails/day
Total: 196 emails/day
```

### Example 2: Randomize across 3 domains

```bash
python mailbox_volume_manager.py \
  --token "YOUR_TOKEN" \
  --domains "domain1.com,domain2.com,domain3.com" \
  --randomize
```

### Example 3: Preview changes without updating

```bash
python mailbox_volume_manager.py \
  --token "YOUR_TOKEN" \
  --domains "domain.com" \
  --target-volume 150 \
  --dry-run
```

### Example 4: Use in Python script

```python
from mailbox_volume_manager import MailboxVolumeManager

manager = MailboxVolumeManager(token="YOUR_TOKEN")

# Randomize and apply
results = manager.batch_update_domains(
    domains=["domain1.com", "domain2.com"],
    randomize=True
)

# Check results
for domain, result in results.items():
    if "error" not in result:
        print(f"{domain}: {result['expected_volume']} emails/day")
```

---

## Configuration

### Environment Variable

```bash
export INSTANTLY_TOKEN="YOUR_BASE64_TOKEN"

python mailbox_volume_manager.py \
  --token $INSTANTLY_TOKEN \
  --domains "domain.com" \
  --target-volume 100
```

### Config File (~/.instantly_keys.json)

```json
{
  "main": {
    "token": "base64_token_here"
  },
  "backup": {
    "token": "another_token"
  }
}
```

Extract with:
```bash
jq -r '.main.token' ~/.instantly_keys.json
```

---

## Volume Guidelines

### Recommended Distributions

| Use Case | Range | Example |
|----------|-------|---------|
| Natural/Organic | 0-4 | Randomize mode |
| Low volume | 0-2 | 50 emails/day per domain |
| Medium volume | 0-3 | 75 emails/day per domain |
| High volume | 0-4 | 100+ emails/day per domain |

### Safe Limits

- **Max per mailbox**: 4 emails/day (settable in Instantly UI)
- **Max per domain**: Depends on SPF/DKIM setup and ISP acceptance
- **Rate limit**: 100 requests/minute on Instantly API
- **Batch size**: ~40-50 mailboxes per request

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `401 Unauthorized` | Token must be base64 encoded (full string, not decoded) |
| `No mailboxes found` | Check domain spelling; verify mailboxes are enabled in Instantly |
| `Rate limit (429)` | Instantly allows 100 reqs/min; space out bulk operations |
| `AttributeError` | Ensure requests library is installed: `pip install requests` |

---

## For Teammates

### Share This Repo

```bash
# Clone
git clone https://github.com/krishnaraj70195-oss/mailbox-volume-randomizer.git
cd mailbox-volume-randomizer

# Install
pip install -r requirements.txt

# Add your token to ~/.instantly_keys.json
# Then use the tool
```

### Quick Integration

```bash
# Use directly in scripts
python mailbox_volume_manager.py --token $INSTANTLY_TOKEN --domains "domain.com" --target-volume 100
```

---

## Support

For issues or questions:
1. Check token format (must be base64, full string)
2. Verify domain spelling and mailbox status in Instantly
3. Test with `--dry-run` first to preview changes
4. Check API status at dashboard.instantly.ai

---

## Version History

- **v1.0** (May 9, 2026) - Initial release, tested with 98 mailboxes
