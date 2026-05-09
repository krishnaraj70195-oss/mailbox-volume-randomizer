# Mailbox Volume Randomizer

Manage daily sending volumes for Instantly.ai mailboxes to create natural sending patterns or hit specific daily targets.

## Features

- ✅ **Randomize volumes** (0-4 range) for organic-looking sending patterns
- ✅ **Set target volumes** (e.g., 100 emails/day per domain)
- ✅ **Multi-domain support** - update multiple domains in one command
- ✅ **Dry-run mode** - preview changes before applying
- ✅ **Natural distribution** - fewer mailboxes at max limit
- ✅ **Batch operations** - update 49+ mailboxes efficiently
- ✅ **Python API** - use in scripts or notebooks
- ✅ **CLI tool** - command-line interface with clear output

## Quick Start

### 1. Install

```bash
git clone https://github.com/krishnaraj70195-oss/mailbox-volume-randomizer.git
cd mailbox-volume-randomizer
pip install -r requirements.txt
```

### 2. Get Your API Token

- Go to Instantly → Settings → API Keys
- Create v2 token (full base64 string)
- Save to `~/.instantly_keys.json`

### 3. Run

**Randomize volumes (natural pattern):**
```bash
python mailbox_volume_manager.py \
  --token "YOUR_TOKEN" \
  --domains "withamanacqs.com,heyamanacqs.com" \
  --randomize
```

**Set target daily volume:**
```bash
python mailbox_volume_manager.py \
  --token "YOUR_TOKEN" \
  --domains "withamanacqs.com,heyamanacqs.com" \
  --target-volume 100
```

## Usage

### CLI

```bash
# Randomize volumes across domains
python mailbox_volume_manager.py \
  --token "base64_token" \
  --domains "domain1.com,domain2.com" \
  --randomize

# Set specific target per domain (100 emails/day)
python mailbox_volume_manager.py \
  --token "base64_token" \
  --domains "domain1.com,domain2.com" \
  --target-volume 100

# Preview changes without updating
python mailbox_volume_manager.py \
  --token "base64_token" \
  --domains "domain1.com" \
  --target-volume 100 \
  --dry-run
```

### Python API

```python
from mailbox_volume_manager import MailboxVolumeManager

manager = MailboxVolumeManager(token="YOUR_TOKEN")

# Update multiple domains with target volume
results = manager.batch_update_domains(
    domains=["domain1.com", "domain2.com"],
    target_volume=100
)

# Check results
print(f"Total daily volume: {results['summary']['total_daily_volume']} emails")
```

## Volume Modes

### Randomize Mode
Distributes volumes randomly across 0-4 for natural-looking patterns:
- 30% at 0 emails/day
- 20% at 1 email/day
- 20% at 2 emails/day
- 20% at 3 emails/day
- 10% at 4 emails/day (fewer at max)

### Target Mode
Distributes volumes to hit a specific daily total per domain. For 49 mailboxes targeting 100 emails:
- 6 at 0 = 0 emails
- 8 at 1 = 8 emails
- 20 at 2 = 40 emails
- 10 at 3 = 30 emails
- 5 at 4 = 20 emails
- **Total: 98 emails/day**

## Examples

### Example 1: Two domains, 100 emails each

```bash
python mailbox_volume_manager.py \
  --token "$(cat ~/.instantly_keys.json | jq -r .main.token)" \
  --domains "withamanacqs.com,heyamanacqs.com" \
  --target-volume 100
```

Output:
```
withamanacqs.com: 98 emails/day (49 mailboxes)
heyamanacqs.com: 98 emails/day (49 mailboxes)
Total: 196 emails/day
```

### Example 2: Randomize across multiple domains

```bash
python mailbox_volume_manager.py \
  --token "YOUR_TOKEN" \
  --domains "domain1.com,domain2.com,domain3.com,domain4.com" \
  --randomize
```

### Example 3: Use in Python

```python
from mailbox_volume_manager import MailboxVolumeManager

manager = MailboxVolumeManager(token="YOUR_TOKEN")

# Get all mailboxes
mailboxes = manager.get_all_mailboxes()

# Filter by domain
domain_mailboxes = manager.filter_by_domain(mailboxes, "domain.com")

# Generate volumes
volumes = manager.randomize_volumes(len(domain_mailboxes))

# Apply
result = manager.apply_volumes(domain_mailboxes, volumes)
print(f"Updated: {result['successful']}/{result['total']}")
print(f"Total daily volume: {result['expected_volume']} emails")
```

## Configuration

### Using Environment Variables

```bash
export INSTANTLY_TOKEN="YOUR_BASE64_TOKEN"

python mailbox_volume_manager.py \
  --token $INSTANTLY_TOKEN \
  --domains "domain.com" \
  --target-volume 100
```

### Using Config File

Create `~/.instantly_keys.json`:

```json
{
  "main": {
    "token": "base64_token_here"
  },
  "backup": {
    "token": "another_base64_token"
  }
}
```

Extract token:
```bash
jq -r '.main.token' ~/.instantly_keys.json
```

## API Reference

### MailboxVolumeManager

#### `get_all_mailboxes()`
Fetch all mailboxes with pagination

```python
mailboxes = manager.get_all_mailboxes()
# Returns: List[Dict] with 515 mailboxes
```

#### `filter_by_domains(mailboxes, domains)`
Filter mailboxes by list of domains

```python
target = manager.filter_by_domains(mailboxes, ["domain1.com", "domain2.com"])
# Returns: 98 mailboxes from both domains
```

#### `randomize_volumes(count, distribution)`
Generate randomized volumes

```python
volumes = manager.randomize_volumes(49)
# Returns: [0, 1, 2, 3, 4, ...] randomized
```

#### `get_target_distribution(target_volume, count)`
Generate volumes for specific daily target

```python
volumes = manager.get_target_distribution(target_volume=100, mailbox_count=49)
# Returns: [0,0,0,0,0,0,1,1,...] totaling ~100
```

#### `apply_volumes(mailboxes, volumes, dry_run)`
Apply volumes to mailboxes

```python
result = manager.apply_volumes(mailboxes, volumes)
# Returns: {"successful": 49, "failed": 0, "expected_volume": 98}
```

#### `batch_update_domains(domains, target_volume, randomize, dry_run)`
Update multiple domains in one call

```python
results = manager.batch_update_domains(
    domains=["domain1.com", "domain2.com"],
    target_volume=100,
    randomize=False,
    dry_run=False
)
```

## Best Practices

1. **Always dry-run first** - Test with `--dry-run` before making changes
2. **Use target mode for predictability** - If you need consistent daily volume
3. **Use randomize for organic patterns** - Vary volumes to avoid detection
4. **Check mailbox status** - Ensure mailboxes are enabled in Instantly before updating
5. **Respect rate limits** - Instantly allows 100 reqs/min; batch operations efficiently
6. **Monitor sends** - Use Instantly dashboard to verify volumes are working

## Troubleshooting

**401 Unauthorized**
- Token must be base64 encoded (full string, not decoded)
- Get full token from Instantly API Keys page

**No mailboxes found**
- Check domain spelling matches exactly
- Verify mailboxes are enabled in Instantly
- Run `--dry-run` to see what would be processed

**Rate limit hit (429)**
- Wait 60 seconds and retry
- Instantly allows 100 requests/minute
- Space out bulk operations

## Requirements

- Python 3.7+
- `requests` library

```bash
pip install -r requirements.txt
```

## Support

For issues or questions:
1. Check token format and domain spelling
2. Test with `--dry-run` to preview
3. Review SKILL.md for detailed documentation
4. Check Instantly API status and dashboard

## License

MIT

## Version

v1.0 (May 2026)
