# GitHub Actions Secrets Configuration Examples

This file shows examples of the secrets you need to configure for the bots.

## GitHub Repository Settings

### Secrets (Settings → Secrets and variables → Actions → Secrets)

#### For Mastodon Bot:
```
MASTODON_INSTANCE=mastodon.social
MASTODON_ACCESS_TOKEN=your_mastodon_access_token_here
MASTODON_VISIBILITY=unlisted  # Optional: public, unlisted, private, or direct
GITHUB_REPO_OWNER=dotnet
GITHUB_REPO_NAME=runtime
```

#### For Bluesky Bot:
```
BLUESKY_HANDLE=yourhandle.bsky.social
BLUESKY_APP_PASSWORD=your_bluesky_app_password_here
GITHUB_REPO_OWNER=dotnet
GITHUB_REPO_NAME=runtime
```

**Note**: No variables are needed! The bots use time-based filtering instead of persistent state.

## How to Get Credentials

### Mastodon Access Token
1. Go to your Mastodon instance (e.g., https://mastodon.social)
2. Settings → Development → New Application
3. Name: "GitHub Issues Bot"
4. Scopes: `read:statuses` and `write:statuses`
5. Save and copy the access token

### Bluesky App Password
1. Log in to Bluesky
2. Settings → App Passwords
3. Add App Password
4. Name: "GitHub Issues Bot"
5. Copy the generated password (you won't see it again!)

## Important Notes

- Never commit secrets to your repository
- The `GITHUB_TOKEN` is automatically provided by GitHub Actions for API rate limit improvements
- No persistent state or variables are needed - the bots use time-based filtering
- Secrets cannot be read or updated by workflows, only used
