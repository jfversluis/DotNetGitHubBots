#!/usr/bin/env python3
"""
Mastodon GitHub Bot
Fetches new issues/PRs from a GitHub repository and posts them to Mastodon.
Uses a tracking issue in the bot repository for persistence.
"""

import os
import sys
import json
import requests
from mastodon import Mastodon

def get_env_var(name, default=None, required=True):
    """Get environment variable with validation."""
    value = os.environ.get(name, default)
    if required and not value:
        print(f"Error: Required environment variable {name} is not set", file=sys.stderr)
        sys.exit(1)
    return value

def get_tracking_issue(bot_repo_owner, bot_repo_name, github_token, tracking_title):
    """Get or create the tracking issue for storing posted issue numbers."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {github_token}"
    }
    
    # Search for existing tracking issue
    search_url = f"https://api.github.com/search/issues"
    params = {
        "q": f'repo:{bot_repo_owner}/{bot_repo_name} is:issue in:title "{tracking_title}"'
    }
    
    try:
        response = requests.get(search_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        results = response.json()
        
        if results['total_count'] > 0:
            # Found existing tracking issue
            issue = results['items'][0]
            print(f"Found existing tracking issue: #{issue['number']}")
            return issue
        
        # Create new tracking issue
        print("Creating new tracking issue for state persistence...")
        create_url = f"https://api.github.com/repos/{bot_repo_owner}/{bot_repo_name}/issues"
        data = {
            "title": tracking_title,
            "body": json.dumps({"posted_issues": [], "last_updated": None}),
            "labels": ["bot-state"]
        }
        
        response = requests.post(create_url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        issue = response.json()
        print(f"Created tracking issue: #{issue['number']}")
        return issue
        
    except requests.exceptions.RequestException as e:
        print(f"Error managing tracking issue: {e}", file=sys.stderr)
        sys.exit(1)

def get_posted_issues(tracking_issue):
    """Extract the list of posted issue numbers from tracking issue."""
    try:
        body = tracking_issue.get('body', '{}')
        state = json.loads(body)
        return set(state.get('posted_issues', []))
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Warning: Could not parse tracking issue body, starting fresh: {e}")
        return set()

def update_tracking_issue(bot_repo_owner, bot_repo_name, github_token, tracking_issue_number, posted_issues):
    """Update the tracking issue with new posted issue numbers."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {github_token}"
    }
    
    url = f"https://api.github.com/repos/{bot_repo_owner}/{bot_repo_name}/issues/{tracking_issue_number}"
    
    from datetime import datetime
    state = {
        "posted_issues": sorted(list(posted_issues)),
        "last_updated": datetime.utcnow().isoformat()
    }
    
    data = {
        "body": json.dumps(state, indent=2)
    }
    
    try:
        response = requests.patch(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"Updated tracking issue with {len(posted_issues)} posted issues")
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not update tracking issue: {e}", file=sys.stderr)

def get_target_issues(repo_owner, repo_name, github_token):
    """Fetch open issues and PRs from the target GitHub repository."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    
    params = {
        "state": "open",
        "sort": "created",
        "direction": "desc",
        "per_page": 100
    }
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {github_token}"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        issues = response.json()
        
        # Sort ascending by number for chronological posting
        issues.sort(key=lambda x: x['number'])
        
        return issues
    except requests.exceptions.RequestException as e:
        print(f"Error fetching issues from GitHub: {e}", file=sys.stderr)
        sys.exit(1)

def post_to_mastodon(mastodon_client, issue, visibility):
    """Post an issue/PR to Mastodon."""
    # Determine if it's a PR or issue
    issue_type = "PR" if "pull_request" in issue else "Issue"
    
    # Format the post text
    text = f"{issue['title']} ({issue['number']}) {issue['html_url']}"
    
    # Truncate if too long (Mastodon limit is 500 characters)
    if len(text) > 450:
        text = text[:447] + "..."
    
    try:
        status = mastodon_client.status_post(text, visibility=visibility)
        print(f"✓ Posted {issue_type} #{issue['number']}: {issue['title']}")
        print(f"  Mastodon URL: {status['url']}")
        return True
    except Exception as e:
        print(f"✗ Error posting {issue_type} #{issue['number']}: {e}", file=sys.stderr)
        return False

def main():
    """Main function to run the bot."""
    # Get configuration from environment variables
    mastodon_instance = get_env_var("MASTODON_INSTANCE")
    mastodon_access_token = get_env_var("MASTODON_ACCESS_TOKEN")
    target_repo_owner = get_env_var("GITHUB_REPO_OWNER")
    target_repo_name = get_env_var("GITHUB_REPO_NAME")
    visibility = get_env_var("VISIBILITY", default="unlisted", required=False)
    
    # Bot repository for tracking (defaults to this repository)
    bot_repo_owner = get_env_var("BOT_REPO_OWNER", default=target_repo_owner, required=False)
    bot_repo_name = get_env_var("BOT_REPO_NAME", default="DotNetGitHubBots", required=False)
    github_token = get_env_var("GITHUB_TOKEN")
    
    tracking_title = f"Mastodon Bot State - {target_repo_owner}/{target_repo_name}"
    
    print(f"Starting Mastodon GitHub Bot")
    print(f"Target repository: {target_repo_owner}/{target_repo_name}")
    print(f"Bot repository: {bot_repo_owner}/{bot_repo_name}")
    print(f"Mastodon instance: {mastodon_instance}")
    print(f"Visibility: {visibility}")
    print()
    
    # Get or create tracking issue
    tracking_issue = get_tracking_issue(bot_repo_owner, bot_repo_name, github_token, tracking_title)
    posted_issues = get_posted_issues(tracking_issue)
    print(f"Previously posted: {len(posted_issues)} issues")
    print()
    
    # Initialize Mastodon client
    mastodon = Mastodon(
        access_token=mastodon_access_token,
        api_base_url=f"https://{mastodon_instance}"
    )
    
    # Fetch target repository issues
    print("Fetching issues from target repository...")
    all_issues = get_target_issues(target_repo_owner, target_repo_name, github_token)
    
    # Filter out already posted issues
    new_issues = [issue for issue in all_issues if issue['number'] not in posted_issues]
    print(f"Found {len(all_issues)} open issues/PRs, {len(new_issues)} are new")
    print()
    
    if not new_issues:
        print("No new issues to publish")
        return
    
    # Post each new issue to Mastodon
    posted_count = 0
    newly_posted = set()
    
    for issue in new_issues:
        if post_to_mastodon(mastodon, issue, visibility):
            posted_count += 1
            newly_posted.add(issue['number'])
    
    print()
    print(f"Summary: Posted {posted_count} out of {len(new_issues)} new issues/PRs")
    
    # Update tracking issue with newly posted issues
    if newly_posted:
        all_posted = posted_issues | newly_posted
        update_tracking_issue(bot_repo_owner, bot_repo_name, github_token, 
                            tracking_issue['number'], all_posted)
        print(f"Total posted issues tracked: {len(all_posted)}")

if __name__ == "__main__":
    main()
