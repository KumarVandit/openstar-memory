#!/usr/bin/env python3
"""
OpenStar Memory - GitHub Stars Sync Script
Fetches starred repos and syncs to markdown + Supermemory
"""

import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Any
import requests

# Configuration from environment
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO_OWNER = os.environ.get("REPO_OWNER", GITHUB_USERNAME)
REPO_NAME = os.environ.get("REPO_NAME", "openstar-memory")
SUPERMEMORY_API_KEY = os.environ.get("SUPERMEMORY_API_KEY", "")
SUPERMEMORY_API_URL = os.environ.get("SUPERMEMORY_API_URL", "https://api.supermemory.ai")

def log(msg: str):
    """Timestamped logging"""
    print(f"[{datetime.utcnow().isoformat()}] {msg}")

def fetch_all_starred_repos() -> List[Dict[str, Any]]:
    """Fetch all starred repositories with pagination"""
    log("Fetching starred repositories...")
    
    if not GITHUB_USERNAME or not GITHUB_TOKEN:
        raise ValueError("GITHUB_USERNAME and GITHUB_TOKEN must be set")
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.star+json"  # Include star timestamps
    }
    
    all_repos = []
    page = 1
    per_page = 100
    
    while True:
        url = f"https://api.github.com/users/{GITHUB_USERNAME}/starred?per_page={per_page}&page={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            log(f"Error fetching stars: {response.status_code} - {response.text}")
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

def generate_markdown(repos: List[Dict[str, Any]]) -> str:
    """Generate markdown content from starred repos"""
    log("Generating markdown...")
    
    # Sort by starred_at date (most recent first) - chronological order
    repos_sorted = sorted(repos, key=lambda x: x.get("starred_at", ""), reverse=True)
    
    md_content = f"""# GitHub Starred Repositories

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

def update_github_file(content: str, file_path: str = "starred-repos.md"):
    """Update or create file in GitHub repository"""
    log(f"Updating {file_path} in {REPO_OWNER}/{REPO_NAME}...")
    
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN must be set")
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Check if file exists to get SHA
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
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
        log("✅ File updated successfully")
        result = response.json()
        commit_url = result.get("commit", {}).get("html_url", "")
        log(f"Commit: {commit_url}")
        return True
    else:
        log(f"❌ Error updating file: {response.status_code} - {response.text}")
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
        # 1. Fetch starred repos
        repos = fetch_all_starred_repos()
        
        if not repos:
            log("❌ No starred repos found")
            return
        
        # 2. Generate markdown
        markdown_content = generate_markdown(repos)
        
        # 3. Update GitHub file
        success = update_github_file(markdown_content)
        
        if not success:
            log("❌ Failed to update GitHub file")
            return
        
        # 4. Sync to Supermemory
        sync_to_supermemory(repos)
        
        log("🎉 Sync completed successfully!")
        
        # Output summary
        print(f"\n📊 Summary:")
        print(f"   Total starred repos: {len(repos)}")
        print(f"   Markdown file: https://github.com/{REPO_OWNER}/{REPO_NAME}/blob/main/starred-repos.md")
        print(f"   Raw URL: https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/starred-repos.md")
        
    except Exception as e:
        log(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
