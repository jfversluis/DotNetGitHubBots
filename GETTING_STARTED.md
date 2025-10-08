# Getting Started - Step by Step

This guide will walk you through setting up the GitHub bots from scratch.

## Prerequisites

- A GitHub account with a repository to monitor
- A Mastodon account (for Mastodon bot)
- A Bluesky account (for Bluesky bot)

## Step 1: Get Your Credentials

### For Mastodon Bot:

1. **Create a Mastodon App**:
   - Go to your Mastodon instance (e.g., `https://mastodon.social`)
   - Navigate to: Settings → Development → New Application
   - Fill in:
     - Application name: `GitHub Issues Bot`
     - Scopes: Select `read:statuses` and `write:statuses`
   - Click "Submit"
   - Copy the **access token** (keep it safe!)

2. **Note your Mastodon instance**:
   - Example: `mastodon.social` (without `https://`)

### For Bluesky Bot:

1. **Create an App Password**:
   - Go to Bluesky settings
   - Navigate to: Settings → App Passwords
   - Click "Add App Password"
   - Name it: `GitHub Issues Bot`
   - Copy the generated password (you won't see it again!)

2. **Note your handle**:
   - Example: `yourname.bsky.social`

## Step 2: Configure GitHub Secrets

1. Go to your GitHub repository
2. Click: Settings → Secrets and variables → Actions
3. Click the "Secrets" tab
4. Click "New repository secret"

### For Mastodon (add these secrets):

| Secret Name | Example Value |
|-------------|---------------|
| `MASTODON_INSTANCE` | `mastodon.social` |
| `MASTODON_ACCESS_TOKEN` | `your_mastodon_access_token` |
| `MASTODON_VISIBILITY` | `unlisted` (optional) |
| `GITHUB_REPO_OWNER` | `dotnet` |
| `GITHUB_REPO_NAME` | `runtime` |

### For Bluesky (add these secrets):

| Secret Name | Example Value |
|-------------|---------------|
| `BLUESKY_HANDLE` | `yourname.bsky.social` |
| `BLUESKY_APP_PASSWORD` | `your_bluesky_app_password` |
| `GITHUB_REPO_OWNER` | `dotnet` |
| `GITHUB_REPO_NAME` | `runtime` |

**Note**: You can reuse `GITHUB_REPO_OWNER` and `GITHUB_REPO_NAME` for both bots if monitoring the same repository.

## Step 3: Test the Bots

1. Go to the "Actions" tab in your repository
2. You should see two workflows:
   - "Mastodon GitHub Bot"
   - "Bluesky GitHub Bot"

3. **Test Mastodon Bot**:
   - Click on "Mastodon GitHub Bot"
   - Click "Run workflow" dropdown
   - Click the green "Run workflow" button
   - Wait a few seconds, then refresh
   - Click on the run to see logs

4. **Test Bluesky Bot**:
   - Click on "Bluesky GitHub Bot"
   - Click "Run workflow" dropdown
   - Click the green "Run workflow" button
   - Wait a few seconds, then refresh
   - Click on the run to see logs

## Step 4: Check the Results

### Successful Run:
- You should see green checkmarks
- Check your Mastodon/Bluesky feed for new posts
- The bot will have posted any issues created in the last 10 minutes

### Failed Run:
- Click on the failed run to see error logs
- Common issues:
  - Invalid credentials
  - Missing secrets
  - Wrong repository owner/name
  - No new issues in the last 10 minutes

## Step 5: Verify Scheduled Runs

The bots will now run automatically every 5 minutes. You can:
- Monitor runs in the Actions tab
- Adjust the schedule in the workflow files if needed
- Disable/enable workflows as needed

## Troubleshooting

### "Error: Required environment variable X is not set"
- Go to Settings → Secrets and variables → Actions
- Verify all required secrets are set
- Check spelling and capitalization

### "No new issues to publish"
- This is normal if there are no new issues created in the last 10 minutes
- The bot checks issues created within the last 10 minutes by default
- If you want to test, create a new issue and run the workflow manually

### "Invalid credentials"
- Mastodon: Regenerate access token and update secret
- Bluesky: Create new app password and update secret
- GitHub: Check repository owner/name are correct

### Posts not appearing on timeline
- Mastodon: Check visibility setting (try `public` instead of `unlisted`)
- Bluesky: Check your profile to see if posts are there
- Both: Verify you're looking at the correct account

## Next Steps

Once everything is working:

1. **Adjust Schedule**: Edit workflow files to change frequency
2. **Customize Posts**: Modify Python scripts to change post format
3. **Monitor Multiple Repos**: Create additional workflow files
4. **Add Filters**: Modify scripts to filter issues by label, author, etc.

See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for more customization options.

## Need Help?

- Review the [README.md](README.md) for detailed documentation
- Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common tasks
- Review [IMPLEMENTATION.md](IMPLEMENTATION.md) for technical details
- Check workflow logs in the Actions tab for specific errors

## Verification Checklist

Before asking for help, verify:

- [ ] All required secrets are set in GitHub
- [ ] Workflow files are present in `.github/workflows/`
- [ ] You've tried running the workflow manually
- [ ] You've checked the workflow logs for errors
- [ ] Repository owner and name are correct
- [ ] Credentials are valid and not expired
- [ ] Repository has had new issues/PRs in the last 10 minutes (for testing)

---

Congratulations! Your bots should now be posting GitHub issues to Mastodon and Bluesky automatically! 🎉
