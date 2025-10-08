#!/usr/bin/env python3
"""
Bluesky GitHub Bot
Fetches new issues/PRs from a GitHub repository and posts them to Bluesky.
"""

import os
import sys
import requests
from datetime import datetime, timedelta
from atproto import Client

def get_env_var(name, default=None, required=True):
    """Get environment variable with validation."""
    value = os.environ.get(name, default)
    if required and not value:
        print(f"Error: Required environment variable {name} is not set", file=sys.stderr)
        sys.exit(1)
    return value

def get_recent_issues(repo_owner, repo_name, since_minutes=10):
    """Fetch issues and PRs from GitHub created in the last N minutes."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    
    # Calculate the time threshold
    since_time = datetime.utcnow() - timedelta(minutes=since_minutes)
    since_iso = since_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    params = {
        "state": "all",  # Get both open and closed to avoid missing any
        "sort": "created",
        "direction": "desc",
        "since": since_iso,
        "per_page": 100
    }
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Add GitHub token if available for higher rate limits
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
    
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

def post_to_bluesky(bluesky_client, issue, posted_ids):
    """Post an issue/PR to Bluesky if not already posted."""
    issue_id = issue['number']
    
    # Check if already posted in this run (duplicate prevention)
    if issue_id in posted_ids:
        print(f"⊘ Skipping duplicate #{issue_id}: {issue['title']}")
        return False
    
    # Determine if it's a PR or issue
    issue_type = "PR" if "pull_request" in issue else "Issue"
    
    # Format the post text
    text = f"{issue['title']} ({issue['number']}) {issue['html_url']}"
    
    # Truncate if too long (Bluesky limit is 300 characters)
    if len(text) > 280:
        text = text[:277] + "..."
    
    try:
        bluesky_client.send_post(text=text)
        print(f"✓ Posted {issue_type} #{issue['number']}: {issue['title']}")
        posted_ids.add(issue_id)
        return True
    except Exception as e:
        print(f"✗ Error posting {issue_type} #{issue['number']}: {e}", file=sys.stderr)
        return False

def main():
    """Main function to run the bot."""
    # Get configuration from environment variables
    bluesky_handle = get_env_var("BLUESKY_HANDLE")
    bluesky_app_password = get_env_var("BLUESKY_APP_PASSWORD")
    repo_owner = get_env_var("GITHUB_REPO_OWNER")
    repo_name = get_env_var("GITHUB_REPO_NAME")
    
    # Get the interval (default to 10 minutes to cover 2 workflow runs at 5-minute intervals)
    interval_minutes = int(get_env_var("INTERVAL_MINUTES", default="10", required=False))
    
    print(f"Starting Bluesky GitHub Bot")
    print(f"Repository: {repo_owner}/{repo_name}")
    print(f"Checking for issues created in the last {interval_minutes} minutes")
    print(f"Bluesky handle: {bluesky_handle}")
    print()
    
    # Initialize Bluesky client
    try:
        client = Client()
        client.login(bluesky_handle, bluesky_app_password)
        print("Successfully logged in to Bluesky")
    except Exception as e:
        print(f"Error logging in to Bluesky: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Fetch recent issues
    print(f"Fetching issues from the last {interval_minutes} minutes...")
    recent_issues = get_recent_issues(repo_owner, repo_name, interval_minutes)
    print(f"Found {len(recent_issues)} issues/PRs created recently")
    print()
    
    if not recent_issues:
        print("No new issues to publish")
        return
    
    # Post each issue to Bluesky with duplicate tracking
    posted_count = 0
    posted_ids = set()
    
    for issue in recent_issues:
        if post_to_bluesky(client, issue, posted_ids):
            posted_count += 1
    
    print()
    print(f"Summary: Posted {posted_count} out of {len(recent_issues)} issues/PRs")

if __name__ == "__main__":
    main()
