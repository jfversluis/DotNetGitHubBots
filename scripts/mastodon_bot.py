#!/usr/bin/env python3
"""
Mastodon GitHub Bot
Fetches new issues/PRs from a GitHub repository and posts them to Mastodon.
"""

import os
import sys
import requests
from mastodon import Mastodon

def get_env_var(name, default=None, required=True):
    """Get environment variable with validation."""
    value = os.environ.get(name, default)
    if required and not value:
        print(f"Error: Required environment variable {name} is not set", file=sys.stderr)
        sys.exit(1)
    return value

def get_unpublished_issues(repo_owner, repo_name, last_issue_number):
    """Fetch new issues and PRs from GitHub that haven't been published yet."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    params = {
        "state": "open",
        "sort": "created",
        "direction": "desc",
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
        
        # Filter issues newer than last_issue_number and sort ascending by number
        new_issues = [
            issue for issue in issues 
            if issue['number'] > last_issue_number
        ]
        new_issues.sort(key=lambda x: x['number'])
        
        return new_issues
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
    repo_owner = get_env_var("GITHUB_REPO_OWNER")
    repo_name = get_env_var("GITHUB_REPO_NAME")
    visibility = get_env_var("VISIBILITY", default="unlisted", required=False)
    last_issue_number = int(get_env_var("LAST_ISSUE_NUMBER", default="0", required=False))
    
    print(f"Starting Mastodon GitHub Bot")
    print(f"Repository: {repo_owner}/{repo_name}")
    print(f"Last published issue number: {last_issue_number}")
    print(f"Mastodon instance: {mastodon_instance}")
    print(f"Visibility: {visibility}")
    print()
    
    # Initialize Mastodon client
    mastodon = Mastodon(
        access_token=mastodon_access_token,
        api_base_url=f"https://{mastodon_instance}"
    )
    
    # Fetch unpublished issues
    print("Fetching new issues from GitHub...")
    new_issues = get_unpublished_issues(repo_owner, repo_name, last_issue_number)
    print(f"Found {len(new_issues)} new issues/PRs to publish")
    print()
    
    if not new_issues:
        print("No new issues to publish")
        return
    
    # Post each issue to Mastodon
    posted_count = 0
    latest_issue_number = last_issue_number
    
    for issue in new_issues:
        if post_to_mastodon(mastodon, issue, visibility):
            posted_count += 1
            latest_issue_number = max(latest_issue_number, issue['number'])
    
    print()
    print(f"Summary: Posted {posted_count} out of {len(new_issues)} issues/PRs")
    
    # Save the latest issue number for next run
    with open("/tmp/last_issue_number.txt", "w") as f:
        f.write(str(latest_issue_number))
    
    print(f"Updated last issue number to: {latest_issue_number}")

if __name__ == "__main__":
    main()
