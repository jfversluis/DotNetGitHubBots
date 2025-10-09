# DotNetGitHubBots

Automated bots that post new GitHub issues and pull requests to social media platforms (Mastodon and Bluesky) using GitHub Actions.

## Features

- 🤖 **Automated posting**: Automatically posts new issues and PRs from multiple GitHub repositories
- 🦣 **Mastodon support**: Posts to Mastodon with configurable visibility
- 🦋 **Bluesky support**: Posts to Bluesky
- ⚙️ **GitHub Actions powered**: Runs entirely on GitHub Actions, no external hosting required
- 🔒 **Secure**: Uses GitHub Secrets for sensitive credentials
- ⏰ **Scheduled runs**: Configurable schedule (default: every 5 minutes)
- 📝 **Persistent state**: Uses GitHub issues in this repository to track posted issues (no external database needed)
- 🔄 **Multi-repository support**: Monitor multiple repositories and post to different social media accounts using a single configuration file

## Setup Instructions

### Configuration File

The bots use a `bot-config.json` file to define repository groups and their corresponding social media accounts. This allows you to:
- Monitor multiple repositories
- Post to different Mastodon/Bluesky accounts for different repository groups
- Easily add or remove repositories without changing code

**Example configuration** (`bot-config.json`):
```json
{
  "bots": [
    {
      "name": "dotnet-core",
      "description": "Bot for .NET Core runtime and extensions repositories",
      "repositories": [
        {"owner": "dotnet", "name": "runtime"},
        {"owner": "dotnet", "name": "extensions"},
        {"owner": "dotnet", "name": "maintenance-packages"}
      ],
      "mastodon": {
        "instance_secret": "MASTODON_INSTANCE_DOTNET_CORE",
        "token_secret": "MASTODON_TOKEN_DOTNET_CORE",
        "visibility_secret": "MASTODON_VISIBILITY_DOTNET_CORE"
      },
      "bluesky": {
        "handle_secret": "BLUESKY_HANDLE_DOTNET_CORE",
        "password_secret": "BLUESKY_PASSWORD_DOTNET_CORE"
      }
    },
    {
      "name": "dotnet-maui",
      "description": "Bot for .NET MAUI repository",
      "repositories": [
        {"owner": "dotnet", "name": "maui"}
      ],
      "mastodon": {
        "instance_secret": "MASTODON_INSTANCE_DOTNET_MAUI",
        "token_secret": "MASTODON_TOKEN_DOTNET_MAUI",
        "visibility_secret": "MASTODON_VISIBILITY_DOTNET_MAUI"
      },
      "bluesky": {
        "handle_secret": "BLUESKY_HANDLE_DOTNET_MAUI",
        "password_secret": "BLUESKY_PASSWORD_DOTNET_MAUI"
      }
    }
  ]
}
```

Each bot group has:
- **name**: Unique identifier for the bot group (used in tracking issue names)
- **repositories**: List of repositories to monitor
- **mastodon/bluesky**: Secret names that contain the credentials for posting

### Prerequisites

1. Multiple GitHub repositories to monitor for issues/PRs
2. One or more Mastodon accounts (for Mastodon bot)
3. One or more Bluesky accounts (for Bluesky bot)

### Mastodon Bot Setup

1. **Get Mastodon Access Tokens**:
   - For each Mastodon account, go to settings (e.g., `https://mastodon.social/settings/applications`)
   - Click "New Application"
   - Give it a name (e.g., "GitHub Issues Bot - .NET Core")
   - Grant the following permissions: `read:statuses` and `write:statuses`
   - Click "Submit" and copy your access token
   - Repeat for each bot group

2. **Configure GitHub Secrets**:
   
   Go to your repository's Settings → Secrets and variables → Actions, then add these secrets for each bot group:
   
   **For the `dotnet-core` bot group:**
   - `MASTODON_INSTANCE_DOTNET_CORE`: Your Mastodon instance (e.g., `mastodon.social`)
   - `MASTODON_TOKEN_DOTNET_CORE`: Your Mastodon access token
   - `MASTODON_VISIBILITY_DOTNET_CORE` (optional): Post visibility (default: `unlisted`)
   
   **For the `dotnet-maui` bot group:**
   - `MASTODON_INSTANCE_DOTNET_MAUI`: Your Mastodon instance
   - `MASTODON_TOKEN_DOTNET_MAUI`: Your Mastodon access token
   - `MASTODON_VISIBILITY_DOTNET_MAUI` (optional): Post visibility (default: `unlisted`)
   
   **Note**: Secret names must match those specified in `bot-config.json`

3. **Configure Repositories**:
   
   Edit `bot-config.json` to add/remove repositories or bot groups as needed. The configuration is applied on each workflow run.

4. **Enable the Workflow**:
   
   The workflow is located at `.github/workflows/mastodon-bot.yml` and will run automatically every 5 minutes. You can also trigger it manually from the Actions tab.

### Bluesky Bot Setup

1. **Get Bluesky App Passwords**:
   - For each Bluesky account, log in to Bluesky
   - Go to Settings → App Passwords
   - Create a new App Password (e.g., name it "GitHub Issues Bot - .NET Core")
   - Copy the generated password
   - Repeat for each bot group

2. **Configure GitHub Secrets**:
   
   Go to your repository's Settings → Secrets and variables → Actions, then add these secrets for each bot group:
   
   **For the `dotnet-core` bot group:**
   - `BLUESKY_HANDLE_DOTNET_CORE`: Your Bluesky handle (e.g., `dotnetcore.bsky.social`)
   - `BLUESKY_PASSWORD_DOTNET_CORE`: Your Bluesky app password
   
   **For the `dotnet-maui` bot group:**
   - `BLUESKY_HANDLE_DOTNET_MAUI`: Your Bluesky handle
   - `BLUESKY_PASSWORD_DOTNET_MAUI`: Your Bluesky app password
   
   **Note**: Secret names must match those specified in `bot-config.json`

3. **Configure Repositories**:
   
   Edit `bot-config.json` to add/remove repositories or bot groups as needed. The configuration is applied on each workflow run.

4. **Enable the Workflow**:
   
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
- A tracking issue is automatically created for each bot group (e.g., "Mastodon Bot State - dotnet-core")
- The issue body contains a JSON object with posted issue numbers organized by repository
- Example tracking issue body:
  ```json
  {
    "posted_issues": {
      "dotnet/runtime": [1234, 1235, 1236],
      "dotnet/extensions": [567, 568],
      "dotnet/maintenance-packages": [89, 90]
    },
    "last_updated": "2024-01-15T10:30:00Z"
  }
  ```
- Each run reads the tracking issue to see what's already been posted for each repository
- After posting new issues, the tracking issue is updated
- This provides reliable persistence without needing external databases or GitHub Variables
- The tracking issues are labeled with `bot-state` and the platform name (`mastodon` or `bluesky`) for easy identification
- Different bot groups have separate tracking issues to avoid conflicts

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