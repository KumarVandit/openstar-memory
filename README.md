# 🌟 OpenStar Memory

**MCP Server & Daily Recipe** to sync your GitHub starred repositories into a searchable knowledge graph using [Supermemory](https://github.com/supermemoryai/supermemory).

Never lose track of why you starred that repo. Get instant context when you need it.

---

## ✨ Features

- 🔄 **Daily Auto-Sync** - Automatically fetches new starred repos every day
- 📚 **Knowledge Graph** - Integrates with Supermemory for semantic search
- 📝 **Markdown Export** - Clean, chronological markdown file
- 🔧 **MCP Server** - Works with Claude Desktop, Cursor, and other MCP clients
- 🐳 **Docker Ready** - Deploy locally or in containers
- ⚙️ **Multi-User** - Configurable for any GitHub username

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- GitHub Personal Access Token ([Generate here](https://github.com/settings/tokens))
- Supermemory API Key (optional, for knowledge graph)

### Installation

```bash
# Clone the repository
git clone https://github.com/KumarVandit/openstar-memory.git
cd openstar-memory

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

Edit `.env`:

```bash
GITHUB_USERNAME=your_github_username
GITHUB_TOKEN=ghp_your_token_here
SUPERMEMORY_API_KEY=your_supermemory_api_key  # Optional
SUPERMEMORY_API_URL=https://api.supermemory.ai  # Optional
REPO_OWNER=KumarVandit  # Where to commit the markdown
REPO_NAME=openstar-memory
```

---

## 📖 Usage

### Run Manually

```bash
# Sync starred repos and update markdown
python sync_stars.py

# Run MCP server
python mcp_server.py
```

### Run with Docker

```bash
# Build image
docker build -t openstar-memory .

# Run sync
docker run --env-file .env openstar-memory

# Run with cron (daily at 2 AM)
docker-compose up -d
```

### Run as Daily Cron Job (Local)

```bash
# Add to crontab
crontab -e

# Run every day at 2 AM
0 2 * * * cd /path/to/openstar-memory && /usr/bin/python3 sync_stars.py >> /var/log/openstar-memory.log 2>&1
```

---

## 🔌 MCP Server Integration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "openstar-memory": {
      "command": "python",
      "args": ["/path/to/openstar-memory/mcp_server.py"],
      "env": {
        "GITHUB_USERNAME": "your_username",
        "GITHUB_TOKEN": "ghp_your_token"
      }
    }
  }
}
```

### Cursor / Other MCP Clients

Configure similarly using the MCP protocol.

---

## 📂 Project Structure

```
openstar-memory/
├── sync_stars.py          # Main sync script
├── mcp_server.py          # MCP server implementation
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker container
├── docker-compose.yml     # Docker Compose config
├── .env.example           # Environment template
├── starred-repos.md       # Generated markdown (auto-created)
└── README.md             # This file
```

---

## 🎯 Output Format

The generated `starred-repos.md` looks like:

```markdown
# GitHub Starred Repositories

Last updated: 2026-02-01 22:52:00 UTC

Total stars: 347

---

## Recently Starred

### [supermemoryai/supermemory](https://github.com/supermemoryai/supermemory)
⭐ 4,521 | 🔤 TypeScript | 📅 Starred: 2026-01-28

Build your own second brain with supermemory. It's a ChatGPT for your bookmarks.

**Topics:** ai, knowledge-graph, memory, second-brain

---

### [composiohq/composio](https://github.com/composiohq/composio)
⭐ 12,345 | 🔤 Python | 📅 Starred: 2026-01-25

Production Ready Toolset for AI Agents

**Topics:** ai, agents, automation, tools

---
```

---

## 🤝 Contributing

Contributions welcome! Open an issue or PR.

---

## 📜 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- [Supermemory](https://github.com/supermemoryai/supermemory) - Knowledge graph backend
- [Composio](https://composio.dev) - Multi-app automation platform
- [GitHub API](https://docs.github.com/en/rest) - Repository data

---

**Built with ❤️ for the open source community**
