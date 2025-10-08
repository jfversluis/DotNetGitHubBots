# Quick Reference Guide

## Initial Setup

### 1. Configure Mastodon Bot

```bash
# In GitHub repository: Settings → Secrets and variables → Actions

# Add Secrets:
MASTODON_INSTANCE = "mastodon.social"
MASTODON_ACCESS_TOKEN = "your_access_token"
MASTODON_VISIBILITY = "unlisted"  # optional
GITHUB_REPO_OWNER = "dotnet"
GITHUB_REPO_NAME = "runtime"

# Add Variables:
MASTODON_LAST_ISSUE_NUMBER = 0
```

### 2. Configure Bluesky Bot

```bash
# In GitHub repository: Settings → Secrets and variables → Actions

# Add Secrets:
BLUESKY_HANDLE = "yourhandle.bsky.social"
BLUESKY_APP_PASSWORD = "your_app_password"
GITHUB_REPO_OWNER = "dotnet"
GITHUB_REPO_NAME = "runtime"

# Add Variables:
BLUESKY_LAST_ISSUE_NUMBER = 0
```

## Common Tasks

### Run Bot Manually

1. Go to Actions tab
2. Select "Mastodon GitHub Bot" or "Bluesky GitHub Bot"
3. Click "Run workflow"
4. Click green "Run workflow" button

### Change Schedule

Edit `.github/workflows/mastodon-bot.yml` or `.github/workflows/bluesky-bot.yml`:

```yaml
# Every 6 hours
cron: '0 */6 * * *'

# Every day at 9 AM UTC
cron: '0 9 * * *'

# Every day at midnight and noon
cron: '0 0,12 * * *'
```

### Monitor Bot Activity

1. Go to Actions tab
2. Click on the workflow name
3. View recent runs and their logs

### Reset Last Issue Number

1. Go to Settings → Secrets and variables → Actions → Variables
2. Edit `MASTODON_LAST_ISSUE_NUMBER` or `BLUESKY_LAST_ISSUE_NUMBER`
3. Set to desired issue number (or 0 to start over)

### Disable a Bot

1. Go to `.github/workflows/`
2. Rename the workflow file to add `.disabled` (e.g., `mastodon-bot.yml.disabled`)
3. Commit and push

Or:

1. Go to Actions tab
2. Select the workflow
3. Click "..." menu → Disable workflow

### Change Post Format

Edit `scripts/mastodon_bot.py` or `scripts/bluesky_bot.py`:

```python
# Current format
text = f"{issue['title']} ({issue['number']}) {issue['html_url']}"

# Example: Add emoji
text = f"🔔 {issue['title']} ({issue['number']}) {issue['html_url']}"

# Example: Add hashtag
text = f"{issue['title']} ({issue['number']}) {issue['html_url']} #dotnet"
```

### Monitor Multiple Repositories

**Option 1: Separate Workflows**
1. Copy workflow file (e.g., `mastodon-bot.yml` → `mastodon-bot-runtime.yml`)
2. Change job name and use different secret names
3. Configure separate secrets and variables

**Option 2: Matrix Strategy**
Edit workflow to use matrix:

```yaml
strategy:
  matrix:
    repo: 
      - owner: dotnet
        name: runtime
      - owner: dotnet
        name: maui
```

## Troubleshooting

### Bot Not Running

**Check:**
- Workflow file is present and valid
- Secrets are configured correctly
- Variables are initialized
- Workflow is not disabled

**View logs:**
1. Actions tab → Select workflow → Click on run → View job logs

### No Posts Appearing

**Possible causes:**
- No new issues in repository
- Last issue number is higher than latest issue
- API credentials are invalid
- Rate limiting

**Fix:**
1. Check last issue number variable
2. Manually trigger workflow to see error messages
3. Verify credentials in secrets

### Duplicate Posts

**Cause:** Variable not updating correctly

**Fix:**
1. Check workflow permissions
2. Ensure `GITHUB_TOKEN` has write access to variables
3. Manually update variable to correct value

### Rate Limiting

**GitHub API:**
- Free: 60 requests/hour (without auth)
- Authenticated: 5,000 requests/hour
- Actions use authenticated requests automatically

**Mastodon:**
- Varies by instance
- Typically: 300 requests per 5 minutes

**Bluesky:**
- 5,000 points per hour per IP
- Creating a post: 3 points

**Solution:** Adjust schedule to run less frequently

## Getting Credentials

### Mastodon Access Token

1. Log in to your Mastodon instance
2. Settings → Development → New Application
3. Name: "GitHub Issues Bot"
4. Permissions: `read:statuses`, `write:statuses`
5. Submit → Copy access token

### Bluesky App Password

1. Log in to Bluesky
2. Settings → App Passwords
3. Add App Password
4. Name: "GitHub Issues Bot"
5. Copy the generated password (shown once!)

## Useful GitHub Actions Features

### View Workflow File from Actions Tab

Actions → Select workflow → "..." menu → View workflow file

### Download Logs

Actions → Select run → "..." menu → Download log archive

### Re-run Failed Jobs

Actions → Select run → Re-run failed jobs

## Testing Locally

### Test Mastodon Bot

```bash
export MASTODON_INSTANCE="mastodon.social"
export MASTODON_ACCESS_TOKEN="your_token"
export GITHUB_REPO_OWNER="dotnet"
export GITHUB_REPO_NAME="runtime"
export VISIBILITY="unlisted"
export LAST_ISSUE_NUMBER="0"

python3 scripts/mastodon_bot.py
```

### Test Bluesky Bot

```bash
export BLUESKY_HANDLE="yourhandle.bsky.social"
export BLUESKY_APP_PASSWORD="your_password"
export GITHUB_REPO_OWNER="dotnet"
export GITHUB_REPO_NAME="runtime"
export LAST_ISSUE_NUMBER="0"

python3 scripts/bluesky_bot.py
```

## Best Practices

1. **Start with a high last issue number** to avoid posting old issues
2. **Test manually first** before relying on scheduled runs
3. **Monitor the Actions tab** regularly for the first few runs
4. **Use unlisted visibility** on Mastodon to avoid spamming followers
5. **Don't set schedule too frequently** to respect API rate limits
6. **Keep credentials secure** - never commit them to the repository
7. **Document any customizations** for future reference

## Support

For issues with:
- **The bots**: Check workflow logs and troubleshooting section
- **GitHub Actions**: https://docs.github.com/en/actions
- **Mastodon API**: https://docs.joinmastodon.org/client/intro/
- **Bluesky API**: https://docs.bsky.app/

## Useful Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cron Expression Guide](https://crontab.guru/)
- [Mastodon.py Documentation](https://mastodonpy.readthedocs.io/)
- [AT Protocol Python SDK](https://github.com/MarshalX/atproto)
- [GitHub API Documentation](https://docs.github.com/en/rest)
