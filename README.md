# DotNetGitHubBots

Automated bots that post new GitHub issues and pull requests to social media platforms (Mastodon and Bluesky) using GitHub Actions.

## Features

- 🤖 **Automated posting**: Automatically posts new issues and PRs from your GitHub repository
- 🦣 **Mastodon support**: Posts to Mastodon with configurable visibility
- 🦋 **Bluesky support**: Posts to Bluesky
- ⚙️ **GitHub Actions powered**: Runs entirely on GitHub Actions, no external hosting required
- 🔒 **Secure**: Uses GitHub Secrets for sensitive credentials
- ⏰ **Scheduled runs**: Configurable schedule (default: every 2 hours)
- 📝 **State management**: Tracks the last published issue to avoid duplicates

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

3. **Initialize the Last Issue Number**:
   
   Go to Settings → Secrets and variables → Actions → Variables tab, and create:
   
   - `MASTODON_LAST_ISSUE_NUMBER`: Set to `0` to start from the beginning, or set to a specific issue number to start from there

4. **Enable the Workflow**:
   
   The workflow is located at `.github/workflows/mastodon-bot.yml` and will run automatically every 2 hours. You can also trigger it manually from the Actions tab.

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

3. **Initialize the Last Issue Number**:
   
   Go to Settings → Secrets and variables → Actions → Variables tab, and create:
   
   - `BLUESKY_LAST_ISSUE_NUMBER`: Set to `0` to start from the beginning, or set to a specific issue number to start from there

4. **Enable the Workflow**:
   
   The workflow is located at `.github/workflows/bluesky-bot.yml` and will run automatically every 2 hours. You can also trigger it manually from the Actions tab.

## How It Works

### Workflow Schedule

Both bots run on a schedule (every 2 hours by default). You can modify the schedule in the workflow files by changing the cron expression:

```yaml
on:
  schedule:
    - cron: '0 */2 * * *'  # Every 2 hours
```

### Issue Tracking

Each bot maintains its own state variable (`MASTODON_LAST_ISSUE_NUMBER` or `BLUESKY_LAST_ISSUE_NUMBER`) to track the last published issue. This prevents duplicate posts and ensures new issues are posted in order.

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
3. Set up different state variables for each

## Troubleshooting

### Bot not posting

1. Check that all required secrets are set correctly
2. Verify the last issue number variable is set
3. Check the Actions tab for error logs
4. Ensure your access tokens haven't expired

### Duplicate posts

This shouldn't happen if the state variable is properly maintained. If it does:
1. Check the variable value in Settings → Actions → Variables
2. Manually set it to the latest published issue number

### Rate limiting

- GitHub API allows 60 requests/hour for unauthenticated requests, 5000/hour for authenticated
- The `GITHUB_TOKEN` is automatically used for authentication
- Mastodon and Bluesky have their own rate limits

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.