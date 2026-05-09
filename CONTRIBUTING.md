# Contributing

## Setup

```bash
git clone https://github.com/krishnaraj70195-oss/mailbox-volume-randomizer.git
cd mailbox-volume-randomizer
pip install -r requirements.txt
```

## Testing

Before committing, test your changes:

```bash
# Test with dry-run
python mailbox_volume_manager.py \
  --token "YOUR_TOKEN" \
  --domains "test-domain.com" \
  --target-volume 100 \
  --dry-run

# Test Python API
python -c "
from mailbox_volume_manager import MailboxVolumeManager
m = MailboxVolumeManager('YOUR_TOKEN')
print('API loaded successfully')
"
```

## Code Style

- Follow PEP 8
- Use type hints where possible
- Add docstrings to new methods
- Keep methods focused and testable

## Commit Messages

- Use clear, descriptive messages
- Reference issues when relevant
- Format: `[feature/fix/docs] Brief description`

Examples:
- `[feature] Add support for custom volume distributions`
- `[fix] Handle pagination edge case`
- `[docs] Update README with examples`

## Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test with `--dry-run` first
5. Commit: `git commit -m "[feature] Description"`
6. Push: `git push origin feature/your-feature`
7. Create Pull Request

## Issues

Report bugs with:
- Clear title
- Steps to reproduce
- Expected behavior
- Actual behavior
- Your token type and domains (without revealing the actual token)
