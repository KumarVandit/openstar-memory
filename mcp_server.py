#!/usr/bin/env python3
"""
OpenStar Memory - MCP Server
Provides MCP interface for querying starred repos

No GitHub token required! Works with public API.
"""

import os
import json
import asyncio
from typing import Any, Optional
import requests

# MCP Server imports (install: pip install mcp)
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("Error: MCP library not installed. Run: pip install mcp")
    exit(1)

# Configuration
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")  # Optional!

# Create MCP server
server = Server("openstar-memory")

def fetch_starred_repos(username: str, query: str = "", limit: int = 10, token: Optional[str] = None) -> list:
    """Fetch starred repositories matching query"""
    if not username:
        return []
    
    headers = {
        "Accept": "application/vnd.github.star+json"
    }
    
    # Add token if provided (for higher rate limits)
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"https://api.github.com/users/{username}/starred?per_page={limit}"
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return []
        
        repos = response.json()
        
        # Filter by query if provided
        if query:
            query_lower = query.lower()
            repos = [
                r for r in repos
                if query_lower in r.get("repo", r).get("full_name", "").lower()
                or query_lower in (r.get("repo", r).get("description", "") or "").lower()
                or any(query_lower in topic.lower() for topic in r.get("repo", r).get("topics", []))
            ]
        
        return repos
    except Exception as e:
        print(f"Error fetching repos: {e}")
        return []

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available MCP tools"""
    return [
        types.Tool(
            name="search_starred_repos",
            description="Search starred repositories by name, description, or topic (for configured GitHub user)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (repo name, description, or topic)"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_recent_stars",
            description="Get most recently starred repositories (for configured GitHub user)",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Number of repos to return (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
        types.Tool(
            name="search_any_user_stars",
            description="Search starred repositories for ANY GitHub user",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "GitHub username to search stars for"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query (repo name, description, or topic)"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10
                    }
                },
                "required": ["username", "query"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle MCP tool calls"""
    
    if name == "search_starred_repos":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        
        if not GITHUB_USERNAME:
            return [types.TextContent(
                type="text",
                text="Error: GITHUB_USERNAME not configured. Set it in environment variables."
            )]
        
        repos = fetch_starred_repos(GITHUB_USERNAME, query=query, limit=limit, token=GITHUB_TOKEN)
        
        result = f"Found {len(repos)} starred repositories matching '{query}' for @{GITHUB_USERNAME}:\n\n"
        
        for item in repos:
            repo = item.get("repo", item)
            result += f"**{repo.get('full_name')}**\n"
            result += f"⭐ {repo.get('stargazers_count', 0)} | {repo.get('language', 'Unknown')}\n"
            result += f"{repo.get('description', 'No description')}\n"
            result += f"🔗 {repo.get('html_url')}\n\n"
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "get_recent_stars":
        limit = arguments.get("limit", 10)
        
        if not GITHUB_USERNAME:
            return [types.TextContent(
                type="text",
                text="Error: GITHUB_USERNAME not configured. Set it in environment variables."
            )]
        
        repos = fetch_starred_repos(GITHUB_USERNAME, limit=limit, token=GITHUB_TOKEN)
        
        result = f"{len(repos)} most recently starred repositories for @{GITHUB_USERNAME}:\n\n"
        
        for item in repos:
            repo = item.get("repo", item)
            starred_at = item.get("starred_at", "Unknown")
            result += f"**{repo.get('full_name')}** (Starred: {starred_at})\n"
            result += f"⭐ {repo.get('stargazers_count', 0)} | {repo.get('language', 'Unknown')}\n"
            result += f"{repo.get('description', 'No description')}\n"
            result += f"🔗 {repo.get('html_url')}\n\n"
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "search_any_user_stars":
        username = arguments.get("username", "")
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        
        if not username:
            return [types.TextContent(
                type="text",
                text="Error: username is required"
            )]
        
        repos = fetch_starred_repos(username, query=query, limit=limit, token=GITHUB_TOKEN)
        
        result = f"Found {len(repos)} starred repositories matching '{query}' for @{username}:\n\n"
        
        for item in repos:
            repo = item.get("repo", item)
            result += f"**{repo.get('full_name')}**\n"
            result += f"⭐ {repo.get('stargazers_count', 0)} | {repo.get('language', 'Unknown')}\n"
            result += f"{repo.get('description', 'No description')}\n"
            result += f"🔗 {repo.get('html_url')}\n\n"
        
        return [types.TextContent(type="text", text=result)]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="openstar-memory",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
