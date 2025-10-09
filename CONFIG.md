# Bot Configuration Guide

## Overview

The `bot-config.json` file defines how the bots monitor repositories and which social media accounts to use for posting. This configuration-based approach allows you to:

- Monitor multiple GitHub repositories
- Group repositories to post to the same social media account
- Use different social media accounts for different repository groups
- Easily add or remove repositories without changing code

## Configuration File Structure

```json
{
  "bots": [
    {
      "name": "bot-group-name",
      "description": "Human-readable description",
      "repositories": [
        {"owner": "org", "name": "repo1"},
        {"owner": "org", "name": "repo2"}
      ],
      "mastodon": {
        "instance_secret": "SECRET_NAME_FOR_INSTANCE",
        "token_secret": "SECRET_NAME_FOR_TOKEN",
        "visibility_secret": "SECRET_NAME_FOR_VISIBILITY"
      },
      "bluesky": {
        "handle_secret": "SECRET_NAME_FOR_HANDLE",
        "password_secret": "SECRET_NAME_FOR_PASSWORD"
      }
    }
  ]
}
```

## Field Descriptions

### Bot Group Level

- **name** (required): Unique identifier for this bot group. Used in tracking issue names. Must be URL-safe (no spaces, special characters).
- **description** (optional): Human-readable description of what this bot group monitors.
- **repositories** (required): Array of repositories this bot group monitors.
- **mastodon** (required for Mastodon bot): Mastodon account configuration.
- **bluesky** (required for Bluesky bot): Bluesky account configuration.

### Repository Configuration

Each repository object has:
- **owner** (required): GitHub username or organization that owns the repository.
- **name** (required): Repository name.

### Mastodon Configuration

- **instance_secret** (required): Name of the GitHub Secret containing the Mastodon instance (e.g., `mastodon.social`).
- **token_secret** (required): Name of the GitHub Secret containing the Mastodon access token.
- **visibility_secret** (optional): Name of the GitHub Secret containing the post visibility (`public`, `unlisted`, `private`, `direct`). Defaults to `unlisted`.

### Bluesky Configuration

- **handle_secret** (required): Name of the GitHub Secret containing the Bluesky handle (e.g., `username.bsky.social`).
- **password_secret** (required): Name of the GitHub Secret containing the Bluesky app password.

## Example Configurations

### Single Repository, Single Account

```json
{
  "bots": [
    {
      "name": "my-project",
      "description": "Bot for my awesome project",
      "repositories": [
        {"owner": "myorg", "name": "myrepo"}
      ],
      "mastodon": {
        "instance_secret": "MASTODON_INSTANCE",
        "token_secret": "MASTODON_TOKEN",
        "visibility_secret": "MASTODON_VISIBILITY"
      },
      "bluesky": {
        "handle_secret": "BLUESKY_HANDLE",
        "password_secret": "BLUESKY_PASSWORD"
      }
    }
  ]
}
```

### Multiple Repositories, Single Account

```json
{
  "bots": [
    {
      "name": "backend-services",
      "description": "All backend service repositories",
      "repositories": [
        {"owner": "myorg", "name": "api-server"},
        {"owner": "myorg", "name": "worker-service"},
        {"owner": "myorg", "name": "database-migrations"}
      ],
      "mastodon": {
        "instance_secret": "MASTODON_INSTANCE_BACKEND",
        "token_secret": "MASTODON_TOKEN_BACKEND",
        "visibility_secret": "MASTODON_VISIBILITY_BACKEND"
      },
      "bluesky": {
        "handle_secret": "BLUESKY_HANDLE_BACKEND",
        "password_secret": "BLUESKY_PASSWORD_BACKEND"
      }
    }
  ]
}
```

### Multiple Groups, Multiple Accounts

```json
{
  "bots": [
    {
      "name": "backend-team",
      "description": "Backend repositories",
      "repositories": [
        {"owner": "myorg", "name": "api"},
        {"owner": "myorg", "name": "worker"}
      ],
      "mastodon": {
        "instance_secret": "MASTODON_INSTANCE_BACKEND",
        "token_secret": "MASTODON_TOKEN_BACKEND",
        "visibility_secret": "MASTODON_VISIBILITY_BACKEND"
      },
      "bluesky": {
        "handle_secret": "BLUESKY_HANDLE_BACKEND",
        "password_secret": "BLUESKY_PASSWORD_BACKEND"
      }
    },
    {
      "name": "frontend-team",
      "description": "Frontend repositories",
      "repositories": [
        {"owner": "myorg", "name": "web-app"},
        {"owner": "myorg", "name": "mobile-app"}
      ],
      "mastodon": {
        "instance_secret": "MASTODON_INSTANCE_FRONTEND",
        "token_secret": "MASTODON_TOKEN_FRONTEND",
        "visibility_secret": "MASTODON_VISIBILITY_FRONTEND"
      },
      "bluesky": {
        "handle_secret": "BLUESKY_HANDLE_FRONTEND",
        "password_secret": "BLUESKY_PASSWORD_FRONTEND"
      }
    }
  ]
}
```

## Adding a New Repository

1. Edit `bot-config.json`
2. Add the repository to the appropriate bot group's `repositories` array:
   ```json
   {"owner": "org-name", "name": "new-repo"}
   ```
3. Commit and push the change
4. The bot will automatically start monitoring the new repository on the next run

## Adding a New Bot Group

1. Edit `bot-config.json`
2. Add a new bot group to the `bots` array with unique `name`
3. Configure the repositories and social media accounts
4. Create the corresponding GitHub Secrets (see next section)
5. Update the workflow files to include the new secrets as environment variables
6. Commit and push the changes

## Required GitHub Secrets

For each bot group defined in `bot-config.json`, you must create the corresponding GitHub Secrets:

### For Mastodon
- Secret with name matching `instance_secret` value
- Secret with name matching `token_secret` value
- (Optional) Secret with name matching `visibility_secret` value

### For Bluesky
- Secret with name matching `handle_secret` value
- Secret with name matching `password_secret` value

### Adding Secrets to Workflows

When you add a new bot group, you must also add its secrets to the workflow files:

**In `.github/workflows/mastodon-bot.yml`:**
```yaml
env:
  # ... existing secrets ...
  
  # New bot group secrets
  MASTODON_INSTANCE_NEWGROUP: ${{ secrets.MASTODON_INSTANCE_NEWGROUP }}
  MASTODON_TOKEN_NEWGROUP: ${{ secrets.MASTODON_TOKEN_NEWGROUP }}
  MASTODON_VISIBILITY_NEWGROUP: ${{ secrets.MASTODON_VISIBILITY_NEWGROUP || 'unlisted' }}
```

**In `.github/workflows/bluesky-bot.yml`:**
```yaml
env:
  # ... existing secrets ...
  
  # New bot group secrets
  BLUESKY_HANDLE_NEWGROUP: ${{ secrets.BLUESKY_HANDLE_NEWGROUP }}
  BLUESKY_PASSWORD_NEWGROUP: ${{ secrets.BLUESKY_PASSWORD_NEWGROUP }}
```

## State Management

Each bot group gets its own tracking issue:
- Mastodon: "Mastodon Bot State - {bot-group-name}"
- Bluesky: "Bluesky Bot State - {bot-group-name}"

The tracking issue stores posted issue numbers per repository:
```json
{
  "posted_issues": {
    "owner1/repo1": [101, 102, 103],
    "owner2/repo2": [45, 46]
  },
  "last_updated": "2024-01-15T10:30:00Z"
}
```

This ensures that:
- Issues from different repositories are tracked separately
- Different bot groups maintain independent state
- You can manually edit tracking issues if needed

## Best Practices

1. **Use descriptive bot group names**: Choose names that clearly indicate what the group monitors (e.g., `dotnet-core`, `frontend-services`).

2. **Keep bot groups focused**: Group repositories that logically belong together and should post to the same account.

3. **Use consistent naming**: Follow a naming convention for your secrets (e.g., `PLATFORM_SETTING_GROUPNAME`).

4. **Document your configuration**: Add a comment in your fork explaining your bot groups and their purpose.

5. **Test incrementally**: When adding new repositories or groups, test with one repository first before adding many.

6. **Monitor tracking issues**: Check the bot-state tracking issues occasionally to ensure they're updating correctly.

## Troubleshooting

### Bot not posting from a specific repository

- Verify the repository owner and name are correct in `bot-config.json`
- Check that the repository exists and is accessible
- Look at the tracking issue to see if issues are being recorded
- Check workflow logs for errors specific to that repository

### Configuration not taking effect

- Ensure `bot-config.json` is committed to the repository
- Check that the file is valid JSON (use a JSON validator)
- Verify the configuration file path matches `BOT_CONFIG_PATH` in workflows (default: `bot-config.json`)

### Missing secrets error

- Verify all secret names in `bot-config.json` match actual GitHub Secrets
- Check that secrets are added to both the repository settings AND the workflow files
- Secret names are case-sensitive

### Tracking issue conflicts

- Each bot group should have a unique `name` field
- If you change a bot group name, a new tracking issue will be created
- Old tracking issues can be closed manually if no longer needed
