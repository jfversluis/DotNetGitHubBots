#!/usr/bin/env python3
"""
Mastodon GitHub Bot
Fetches new issues/PRs from multiple GitHub repositories and posts them to Mastodon.
Uses a tracking issue in the bot repository for persistence.
Supports multiple repository groups with different Mastodon accounts.
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

def load_config(config_path):
    """Load bot configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"Loaded configuration with {len(config['bots'])} bot groups")
        return config
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)

def get_tracking_issue(bot_repo_owner, bot_repo_name, github_token, bot_group_name):
    """Get or create the tracking issue for storing posted issue numbers."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {github_token}"
    }
    
    tracking_title = f"Mastodon Bot State - {bot_group_name}"
    
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
            issue = results['items'][0]
            print(f"  Found existing tracking issue: #{issue['number']}")
            return issue
        
        # Create new tracking issue
        print(f"  Creating new tracking issue for {bot_group_name}...")
        create_url = f"https://api.github.com/repos/{bot_repo_owner}/{bot_repo_name}/issues"
        data = {
            "title": tracking_title,
            "body": json.dumps({"posted_issues": {}, "last_updated": None}, indent=2),
            "labels": ["bot-state", "mastodon"]
        }
        
        response = requests.post(create_url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        issue = response.json()
        print(f"  Created tracking issue: #{issue['number']}")
        return issue
        
    except requests.exceptions.RequestException as e:
        print(f"Error managing tracking issue: {e}", file=sys.stderr)
        sys.exit(1)

def get_posted_issues(tracking_issue):
    """Extract the dict of posted issue numbers from tracking issue."""
    try:
        body = tracking_issue.get('body', '{}')
        state = json.loads(body)
        # Returns dict like {"owner/repo": [1, 2, 3]}
        return state.get('posted_issues', {})
    except (json.JSONDecodeError, ValueError) as e:
        print(f"  Warning: Could not parse tracking issue body, starting fresh: {e}")
        return {}

def update_tracking_issue(bot_repo_owner, bot_repo_name, github_token, tracking_issue_number, posted_issues_dict):
    """Update the tracking issue with new posted issue numbers."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {github_token}"
    }
    
    url = f"https://api.github.com/repos/{bot_repo_owner}/{bot_repo_name}/issues/{tracking_issue_number}"
    
    from datetime import datetime
    state = {
        "posted_issues": posted_issues_dict,
        "last_updated": datetime.utcnow().isoformat()
    }
    
    data = {
        "body": json.dumps(state, indent=2)
    }
    
    try:
        response = requests.patch(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        total_posted = sum(len(issues) for issues in posted_issues_dict.values())
        print(f"  Updated tracking issue with {total_posted} total posted issues across all repos")
    except requests.exceptions.RequestException as e:
        print(f"  Warning: Could not update tracking issue: {e}", file=sys.stderr)

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
        "Authorization": f"token {github_token}"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        issues = response.json()
        
        # Sort ascending by number for chronological posting
        issues.sort(key=lambda x: x['number'])
        
        return issues
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching issues from {repo_owner}/{repo_name}: {e}", file=sys.stderr)
        return []

def post_to_mastodon(mastodon_client, issue, visibility, repo_full_name):
    """Post an issue/PR to Mastodon."""
    issue_type = "PR" if "pull_request" in issue else "Issue"
    
    # Format the post text
    text = f"{issue['title']} ({issue['number']}) {issue['html_url']}"
    
    # Truncate if too long (Mastodon limit is 500 characters)
    if len(text) > 450:
        text = text[:447] + "..."
    
    try:
        status = mastodon_client.status_post(text, visibility=visibility)
        print(f"    ✓ Posted {repo_full_name}#{issue['number']}: {issue['title']}")
        print(f"      Mastodon URL: {status['url']}")
        return True
    except Exception as e:
        print(f"    ✗ Error posting {repo_full_name}#{issue['number']}: {e}", file=sys.stderr)
        return False

def process_bot_group(bot_config, bot_repo_owner, bot_repo_name, github_token):
    """Process one bot group (multiple repos posting to one Mastodon account)."""
    bot_name = bot_config['name']
    print(f"\n{'='*60}")
    print(f"Processing bot group: {bot_name}")
    print(f"{'='*60}")
    
    # Get Mastodon credentials from secrets
    mastodon_instance = get_env_var(bot_config['mastodon']['instance_secret'])
    mastodon_access_token = get_env_var(bot_config['mastodon']['token_secret'])
    visibility = get_env_var(bot_config['mastodon']['visibility_secret'], default="unlisted", required=False)
    
    print(f"Mastodon instance: {mastodon_instance}")
    print(f"Visibility: {visibility}")
    print(f"Repositories: {len(bot_config['repositories'])}")
    
    # Get or create tracking issue for this bot group
    tracking_issue = get_tracking_issue(bot_repo_owner, bot_repo_name, github_token, bot_name)
    posted_issues_dict = get_posted_issues(tracking_issue)
    
    # Initialize Mastodon client
    mastodon = Mastodon(
        access_token=mastodon_access_token,
        api_base_url=f"https://{mastodon_instance}"
    )
    
    total_new_issues = 0
    total_posted = 0
    updated = False
    
    # Process each repository in this bot group
    for repo_config in bot_config['repositories']:
        repo_owner = repo_config['owner']
        repo_name = repo_config['name']
        repo_full_name = f"{repo_owner}/{repo_name}"
        
        print(f"\n  Processing repository: {repo_full_name}")
        
        # Get previously posted issues for this repo
        posted_for_repo = set(posted_issues_dict.get(repo_full_name, []))
        print(f"  Previously posted from this repo: {len(posted_for_repo)} issues")
        
        # Fetch current open issues
        all_issues = get_target_issues(repo_owner, repo_name, github_token)
        new_issues = [issue for issue in all_issues if issue['number'] not in posted_for_repo]
        
        print(f"  Found {len(all_issues)} open issues/PRs, {len(new_issues)} are new")
        
        if new_issues:
            total_new_issues += len(new_issues)
            
            # Post each new issue
            newly_posted = []
            for issue in new_issues:
                if post_to_mastodon(mastodon, issue, visibility, repo_full_name):
                    newly_posted.append(issue['number'])
                    total_posted += 1
            
            # Update tracking for this repo
            if newly_posted:
                all_posted_for_repo = sorted(list(posted_for_repo | set(newly_posted)))
                posted_issues_dict[repo_full_name] = all_posted_for_repo
                updated = True
    
    # Update tracking issue if any new posts were made
    if updated:
        update_tracking_issue(bot_repo_owner, bot_repo_name, github_token, 
                            tracking_issue['number'], posted_issues_dict)
    
    print(f"\nBot group '{bot_name}' summary: Posted {total_posted} out of {total_new_issues} new issues/PRs")
    return total_posted

def main():
    """Main function to run the bot."""
    print("Starting Mastodon GitHub Bot (Multi-Repository)")
    print("=" * 60)
    
    # Get bot repository info
    bot_repo_owner = get_env_var("BOT_REPO_OWNER")
    bot_repo_name = get_env_var("BOT_REPO_NAME")
    github_token = get_env_var("GITHUB_TOKEN")
    config_path = get_env_var("BOT_CONFIG_PATH", default="bot-config.json", required=False)
    
    print(f"Bot repository: {bot_repo_owner}/{bot_repo_name}")
    print(f"Config file: {config_path}")
    
    # Load configuration
    config = load_config(config_path)
    
    # Process each bot group
    total_posted_all = 0
    for bot_config in config['bots']:
        posted_count = process_bot_group(bot_config, bot_repo_owner, bot_repo_name, github_token)
        total_posted_all += posted_count
    
    print(f"\n{'='*60}")
    print(f"All bot groups processed. Total posted: {total_posted_all} issues/PRs")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
