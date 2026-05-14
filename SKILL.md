# Mailbox Rotation Skill

**Status**: ✅ Interactive (Production Ready)  
**Purpose**: Interactively apply randomized daily sending volumes to Instantly.ai mailboxes  
**Input**: Domain, volume range (e.g., 1-6), total sends target  

---

## Quick Start

```bash
python mailbox_rotation_skill.py
```

Then answer three prompts:
1. **Domain**: `amanscaling.com`
2. **Volume range**: `1-6` (or `2-8`, `1-4`, etc.)
3. **Total emails/day**: `250` (or `300`, `500`, etc.)

---

## How It Works

1. **Ask for domain** - Which domain to update?
2. **Ask for range** - What volume range? (1-6, 2-8, 1-4, etc.)
3. **Ask for target** - Total emails/day? (250, 300, 500, etc.)
4. **Generate distribution** - Creates organic random spread across the range
5. **Adjust to target** - Fine-tunes volumes to hit exact daily total
6. **Dry run** - Shows what will be applied
7. **Apply** - Confirms and updates all mailboxes

---

## Examples

### Example 1: Conservative volume (1-4 range, 150 total)

```
Domain: mycompany.com
Range: 1-4
Target: 150
```

Result (25 mailboxes):
- 3 at 1 = 3
- 5 at 2 = 10
- 8 at 3 = 24
- 9 at 4 = 36
- Total: 73 (then adjusted to 150)

### Example 2: Aggressive volume (1-8 range, 500 total)

```
Domain: leadgen.com
Range: 1-8
Target: 500
```

Result (50 mailboxes):
- 2 at 3 = 6
- 8 at 5 = 40
- 15 at 6 = 90
- 12 at 7 = 84
- 13 at 8 = 104
- Total: 500

### Example 3: High volume (2-10 range, 600 total)

```
Domain: bigcampaign.com
Range: 2-10
Target: 600
```

---

## Installation

```bash
# Clone the repo
git clone https://github.com/krishnaraj70195-oss/mailbox-volume-randomizer.git
cd mailbox-volume-randomizer

# Install dependencies
pip install -r requirements.txt

# Run the skill
python mailbox_rotation_skill.py
```

---

## API Token Setup

Add your Instantly API token to `~/.instantly_keys.json`:

```json
{
  "main": {
    "token": "YOUR_BASE64_TOKEN_HERE"
  }
}
```

Or use environment variable:
```bash
export INSTANTLY_TOKEN="YOUR_BASE64_TOKEN"
python mailbox_rotation_skill.py
```

---

## Supported Volume Ranges

- `1-4` - Conservative (light sending)
- `1-6` - Moderate (medium volume)
- `2-8` - Aggressive (higher volume)
- `3-10` - Heavy (very high volume)
- Any custom range: `1-5`, `2-7`, etc.

---

## Best Practices

1. **Start conservative** - Test with 1-4 range and 100-150 total
2. **Dry run first** - Always check the distribution before applying
3. **Organic patterns** - Don't use even distribution (use randomized)
4. **Respect domain reputation** - Gradual increases work better
5. **Monitor sends** - Check Instantly dashboard after applying
6. **Update regularly** - Re-randomize every week or campaign reset

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `No mailboxes found` | Check domain spelling and that mailboxes are enabled in Instantly |
| `401 Unauthorized` | Verify API token is correct base64 string (full token, not decoded) |
| `Invalid range` | Use format: `1-6` or `2-8` (no spaces) |
| `Total too high` | Max = (mailbox_count × max_volume). E.g., 50 mailboxes at 6 max = 300 total |

---

## For Teams

Share this skill with teammates:

```bash
# Clone
git clone https://github.com/krishnaraj70195-oss/mailbox-volume-randomizer.git

# Setup token
echo '{"main": {"token": "YOUR_TOKEN"}}' > ~/.instantly_keys.json

# Run
python mailbox_rotation_skill.py
```

---

## Version History

- **v1.1** (May 14, 2026) - Interactive skill added
- **v1.0** (May 9, 2026) - Initial CLI release
