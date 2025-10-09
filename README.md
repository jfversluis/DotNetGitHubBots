# DotNetGitHubBots

Automated bots that post new GitHub issues and pull requests to social media platforms (Mastodon and Bluesky) using GitHub Actions.

## Features

- 🤖 **Automated posting**: Automatically posts new issues and PRs from your GitHub repository
- 🦣 **Mastodon support**: Posts to Mastodon with configurable visibility
- 🦋 **Bluesky support**: Posts to Bluesky
- ⚙️ **GitHub Actions powered**: Runs entirely on GitHub Actions, no external hosting required
- 🔒 **Secure**: Uses GitHub Secrets for sensitive credentials
- ⏰ **Scheduled runs**: Configurable schedule (default: every 5 minutes)
- 📝 **Persistent state**: Uses GitHub issues in this repository to track posted issues (no external database needed)

## Setup Instructions

### Prerequisites

1. A GitHub repository to monitor for issues/PRs
2. A Mastodon account (for Mastodon bot)
3. A Bluesky account (for Bluesky bot)

### Mastodon Bot Setup

1. **Get Mastodon Access Token**:
   - Go to your Mastodon instance settings (e.g., `https://mastodon.social/settings/applications`)
   - Click "New Application"
   - Give it a name (e.g., "GitHub Issues Bot")
   - Grant the following permissions: `read:statuses` and `write:statuses`
   - Click "Submit" and copy your access token

2. **Configure GitHub Secrets**:
   
   Go to your repository's Settings → Secrets and variables → Actions, then add these secrets:
   
   - `MASTODON_INSTANCE`: Your Mastodon instance (e.g., `mastodon.social`)
   - `MASTODON_ACCESS_TOKEN`: Your Mastodon access token
   - `GITHUB_REPO_OWNER`: The owner/org of the repository to monitor
   - `GITHUB_REPO_NAME`: The name of the repository to monitor
   - `MASTODON_VISIBILITY` (optional): Post visibility (`public`, `unlisted`, `private`, or `direct`). Default: `unlisted`

3. **Enable the Workflow**:
   
   The workflow is located at `.github/workflows/mastodon-bot.yml` and will run automatically every 5 minutes. You can also trigger it manually from the Actions tab.

### Bluesky Bot Setup

1. **Get Bluesky App Password**:
   - Log in to your Bluesky account
   - Go to Settings → App Passwords
   - Create a new App Password
   - Copy the generated password

2. **Configure GitHub Secrets**:
   
   Go to your repository's Settings → Secrets and variables → Actions, then add these secrets:
   
   - `BLUESKY_HANDLE`: Your Bluesky handle (e.g., `username.bsky.social`)
   - `BLUESKY_APP_PASSWORD`: Your Bluesky app password
   - `GITHUB_REPO_OWNER`: The owner/org of the repository to monitor
   - `GITHUB_REPO_NAME`: The name of the repository to monitor

3. **Enable the Workflow**:
   
   The workflow is located at `.github/workflows/bluesky-bot.yml` and will run automatically every 5 minutes. You can also trigger it manually from the Actions tab.

## How It Works

### Workflow Schedule

Both bots run on a schedule (every 5 minutes by default). You can modify the schedule in the workflow files by changing the cron expression:

```yaml
on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes (minimum for GitHub Actions)
```

**Note**: The original MastodonGitHubBot checked every 2 minutes, but GitHub Actions has a minimum cron schedule interval of 5 minutes. This is the closest we can get to the original behavior while using GitHub Actions.

### State Persistence

The bots use GitHub issues in this repository for persistent state tracking:
- A tracking issue is automatically created for each target repository (e.g., "Mastodon Bot State - owner/repo")
- The issue body contains a JSON object with the list of posted issue numbers
- Each run reads the tracking issue to see what's already been posted
- After posting new issues, the tracking issue is updated
- This provides reliable persistence without needing external databases or GitHub Variables
- The tracking issues are labeled with `bot-state` for easy identification

### Manual Trigger

You can manually trigger either bot from the Actions tab:
1. Go to Actions
2. Select the workflow (Mastodon GitHub Bot or Bluesky GitHub Bot)
3. Click "Run workflow"

## Post Format

Posts are formatted as:
```
[Issue/PR Title] ([Number]) [URL]
```

Example:
```
Fix memory leak in data processing (42) https://github.com/owner/repo/issues/42
```

## Customization

### Change Schedule

Edit the cron expression in `.github/workflows/mastodon-bot.yml` or `.github/workflows/bluesky-bot.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
```

### Change Post Format

Modify the `post_to_mastodon()` or `post_to_bluesky()` functions in the respective Python scripts in the `scripts/` directory.

### Monitor Multiple Repositories

You can:
1. Duplicate and rename the workflow files
2. Use different secret names for each repository

## Troubleshooting

### Bot not posting

1. Check that all required secrets are set correctly
2. Check the Actions tab for error logs
3. Ensure your access tokens haven't expired
4. Check that the workflow has `issues: write` permission
5. Look for the tracking issue in the Issues tab (labeled with `bot-state`)

### Duplicate posts

Duplicates should not occur with the GitHub issue-based persistence. If they do:
- Check that the tracking issue exists and is being updated
- Verify the workflow has `issues: write` permission
- Check the tracking issue body to see what's recorded

### Reset bot state

To start over or fix tracking issues:
1. Find the tracking issue (search for "Bot State" in Issues)
2. Edit the issue body to remove specific issue numbers or reset to `{"posted_issues": [], "last_updated": null}`
3. Or close/delete the tracking issue - a new one will be created on next run

### Rate limiting

- GitHub API allows 60 requests/hour for unauthenticated requests, 5000/hour for authenticated
- The `GITHUB_TOKEN` is automatically used for authentication
- Mastodon and Bluesky have their own rate limits
- Running every 5 minutes = 12 runs/hour, well within limits

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.