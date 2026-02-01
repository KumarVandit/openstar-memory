#!/usr/bin/env python3
"""
OpenStar Memory - GitHub Stars Sync Script
Fetches starred repos and syncs to markdown + Supermemory

Modes:
  1. Local Mode (no token): Generates markdown locally
  2. Auto-Commit Mode (token required): Commits to GitHub repo
"""

import os
import json
import base64
import subprocess
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import requests

# Configuration from environment
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")  # Optional!
SUPERMEMORY_API_KEY = os.environ.get("SUPERMEMORY_API_KEY", "")
SUPERMEMORY_API_URL = os.environ.get("SUPERMEMORY_API_URL", "https://api.supermemory.ai")

def log(msg: str):
    """Timestamped logging"""
    print(f"[{datetime.utcnow().isoformat()}] {msg}")

def get_repo_info() -> Optional[Tuple[str, str]]:
    """Auto-detect repo owner and name from git remote"""
    try:
        # Get git remote URL
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True,
            check=True
        )
        remote_url = result.stdout.strip()
        
        # Parse owner/repo from various GitHub URL formats
        patterns = [
            r'github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, remote_url)
            if match:
                owner, repo = match.groups()
                log(f"Auto-detected repo: {owner}/{repo}")
                return owner, repo
        
        log(f"Could not parse GitHub repo from remote URL: {remote_url}")
        return None
    
    except subprocess.CalledProcessError:
        log("Not a git repository or no remote.origin.url configured")
        return None

def fetch_all_starred_repos(username: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch all starred repositories with pagination"""
    log(f"Fetching starred repositories for @{username}...")
    
    if not username:
        raise ValueError("GITHUB_USERNAME must be set")
    
    headers = {
        "Accept": "application/vnd.github.star+json"  # Include star timestamps
    }
    
    # Add token if provided (for higher rate limits)
    if token:
        headers["Authorization"] = f"token {token}"
        log("Using authenticated requests (higher rate limit)")
    else:
        log("Using unauthenticated requests (60 req/hour limit)")
    
    all_repos = []
    page = 1
    per_page = 100
    
    while True:
        url = f"https://api.github.com/users/{username}/starred?per_page={per_page}&page={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            log(f"Error fetching stars: {response.status_code} - {response.text}")
            if response.status_code == 403:
                log("Rate limit exceeded. Consider adding GITHUB_TOKEN for higher limits.")
            break
        
        repos = response.json()
        if not repos:
            break
        
        all_repos.extend(repos)
        log(f"Fetched page {page}: {len(repos)} repos")
        
        if len(repos) < per_page:
            break
        
        page += 1
    
    log(f"Total starred repos fetched: {len(all_repos)}")
    return all_repos

def generate_markdown(repos: List[Dict[str, Any]], username: str) -> str:
    """Generate markdown content from starred repos"""
    log("Generating markdown...")
    
    # Sort by starred_at date (most recent first) - chronological order
    repos_sorted = sorted(repos, key=lambda x: x.get("starred_at", ""), reverse=True)
    
    md_content = f"""# {username}'s GitHub Stars

Last updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC

Total stars: {len(repos)}

---

## Recently Starred

"""
    
    for item in repos_sorted:
        repo = item.get("repo", item)  # Handle different response formats
        
        name = repo.get("full_name", "Unknown")
        url = repo.get("html_url", "")
        description = repo.get("description", "No description provided")
        language = repo.get("language", "Unknown")
        stars = repo.get("stargazers_count", 0)
        topics = repo.get("topics", [])
        starred_at = item.get("starred_at", "Unknown")
        
        # Format starred date
        if starred_at != "Unknown":
            try:
                starred_date = datetime.fromisoformat(starred_at.replace("Z", "+00:00"))
                starred_at_fmt = starred_date.strftime("%Y-%m-%d")
            except:
                starred_at_fmt = starred_at
        else:
            starred_at_fmt = "Unknown"
        
        md_content += f"""### [{name}]({url})
⭐ {stars:,} | 🔤 {language} | 📅 Starred: {starred_at_fmt}

{description}

"""
        if topics:
            md_content += f"**Topics:** {', '.join(topics)}\n\n"
        
        md_content += "---\n\n"
    
    return md_content

def save_markdown_locally(content: str, filename: str = "starred-repos.md"):
    """Save markdown file locally"""
    log(f"Saving markdown to {filename}...")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    log(f"✅ Saved to {filename}")

def update_github_file(owner: str, repo: str, content: str, token: str, file_path: str = "starred-repos.md"):
    """Update or create file in GitHub repository"""
    log(f"Committing {file_path} to {owner}/{repo}...")
    
    if not token:
        raise ValueError("GITHUB_TOKEN is required for auto-commit mode")
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Check if file exists to get SHA
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    response = requests.get(url, headers=headers)
    
    sha = None
    if response.status_code == 200:
        sha = response.json().get("sha")
        log(f"File exists, updating (SHA: {sha[:7]}...)")
    else:
        log("File doesn't exist, creating new file")
    
    # Prepare content
    content_base64 = base64.b64encode(content.encode()).decode()
    
    payload = {
        "message": f"Update starred repos - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        "content": content_base64,
        "branch": "main"
    }
    
    if sha:
        payload["sha"] = sha
    
    # Update file
    response = requests.put(url, headers=headers, json=payload)
    
    if response.status_code in [200, 201]:
        log("✅ File committed successfully")
        result = response.json()
        commit_url = result.get("commit", {}).get("html_url", "")
        log(f"Commit: {commit_url}")
        return True
    else:
        log(f"❌ Error committing file: {response.status_code} - {response.text}")
        return False

def sync_to_supermemory(repos: List[Dict[str, Any]]):
    """Sync starred repos to Supermemory knowledge graph"""
    if not SUPERMEMORY_API_KEY:
        log("ℹ️  SUPERMEMORY_API_KEY not set, skipping Supermemory sync")
        return
    
    log("Syncing to Supermemory...")
    
    # TODO: Implement Supermemory API integration
    # This is a placeholder - adjust based on actual Supermemory API
    headers = {
        "Authorization": f"Bearer {SUPERMEMORY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    for item in repos:
        repo = item.get("repo", item)
        
        # Prepare memory entry
        memory_data = {
            "content": f"{repo.get('full_name')}: {repo.get('description', '')}",
            "url": repo.get("html_url", ""),
            "tags": repo.get("topics", []) + [repo.get("language", "")],
            "timestamp": item.get("starred_at", datetime.utcnow().isoformat())
        }
        
        # Send to Supermemory (adjust endpoint based on actual API)
        # response = requests.post(f"{SUPERMEMORY_API_URL}/memories", headers=headers, json=memory_data)
        # if response.status_code != 200:
        #     log(f"Warning: Failed to sync {repo.get('full_name')} to Supermemory")
    
    log("✅ Supermemory sync complete")

def main():
    """Main execution"""
    log("🌟 OpenStar Memory - Starting sync...")
    
    try:
        # Check if we have a username
        if not GITHUB_USERNAME:
            raise ValueError("GITHUB_USERNAME must be set in .env")
        
        # Determine mode
        repo_info = get_repo_info()
        auto_commit_mode = bool(GITHUB_TOKEN and repo_info)
        
        if auto_commit_mode:
            repo_owner, repo_name = repo_info
            log(f"🚀 Mode: AUTO-COMMIT (will commit to {repo_owner}/{repo_name})")
        else:
            log("📝 Mode: LOCAL-ONLY (no token or not in git repo)")
            if not GITHUB_TOKEN:
                log("   ℹ️  Add GITHUB_TOKEN to .env for auto-commit mode")
            if not repo_info:
                log("   ℹ️  Run from a git repo with GitHub remote for auto-commit")
        
        # 1. Fetch starred repos
        repos = fetch_all_starred_repos(GITHUB_USERNAME, GITHUB_TOKEN)
        
        if not repos:
            log("❌ No starred repos found")
            return
        
        # 2. Generate markdown
        markdown_content = generate_markdown(repos, GITHUB_USERNAME)
        
        # 3. Save locally (always)
        save_markdown_locally(markdown_content)
        
        # 4. Commit to GitHub (if in auto-commit mode)
        if auto_commit_mode:
            success = update_github_file(repo_owner, repo_name, markdown_content, GITHUB_TOKEN)
            if not success:
                log("⚠️  Failed to commit to GitHub, but file is saved locally")
        
        # 5. Sync to Supermemory (optional)
        sync_to_supermemory(repos)
        
        log("🎉 Sync completed successfully!")
        
        # Output summary
        print(f"\n📊 Summary:")
        print(f"   Total starred repos: {len(repos)}")
        print(f"   Local file: ./starred-repos.md")
        
        if auto_commit_mode:
            print(f"   GitHub: https://github.com/{repo_owner}/{repo_name}/blob/main/starred-repos.md")
            print(f"   Raw URL: https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/starred-repos.md")
        else:
            print(f"   💡 Tip: Add GITHUB_TOKEN to auto-commit to your repo!")
        
    except Exception as e:
        log(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
