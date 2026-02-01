# 🌟 OpenStar Memory

**MCP Server & Daily Sync** to track your GitHub starred repositories with zero configuration.

Never lose track of why you starred that repo. Get instant context when you need it.

---

## ✨ Features

- ⚡ **Zero Config** - Just your GitHub username, that's it!
- 🔄 **Two Modes** - Local-only or auto-commit to GitHub
- 📚 **Knowledge Graph** - Integrates with Supermemory for semantic search
- 📝 **Markdown Export** - Clean, chronological markdown file
- 🔧 **MCP Server** - Works with Claude Desktop, Cursor, and other MCP clients
- 🐳 **Docker Ready** - Deploy locally or in containers
- 🔓 **No Token Needed** - Token only required for auto-commit

---

## 🚀 Quick Start

### **The Simplest Way (No Token Required!)**

```bash
# Clone or fork the repo
git clone https://github.com/YOUR_USERNAME/openstar-memory.git
cd openstar-memory

# Install dependencies
pip install -r requirements.txt

# Configure (ONLY 1 REQUIRED VALUE!)
cp .env.example .env
# Edit .env and set: GITHUB_USERNAME=your_username

# Run it!
python sync_stars.py
```

✨ **That's it!** Your `starred-repos.md` is generated locally!

---

## 🔄 Two Modes

### **Mode 1: Local-Only** (No Token)
- ✅ Fetches public starred repos
- ✅ Generates `starred-repos.md` locally
- ✅ Perfect for quick lookups
- ✅ No GitHub token needed

**Setup:**
```bash
# .env
GITHUB_USERNAME=your_username
# That's it!
```

### **Mode 2: Auto-Commit** (Token Required)
- ✅ Everything from Mode 1
- ✅ Auto-commits to your GitHub repo
- ✅ Daily automation ready
- ✅ Raw URL for editors

**Setup:**
```bash
# .env
GITHUB_USERNAME=your_username
GITHUB_TOKEN=ghp_your_token_here  # Get from github.com/settings/tokens
```

---

## 📚 Usage

### Run Locally

```bash
# Just generate markdown
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

# Daily auto-sync
docker-compose up -d
```

### Daily Cron Job

```bash
# Run every day at 2 AM
0 2 * * * cd /path/to/openstar-memory && python sync_stars.py
```

---

## 🔌 MCP Server Integration

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "openstar-memory": {
      "command": "python",
      "args": ["/path/to/openstar-memory/mcp_server.py"],
      "env": {
        "GITHUB_USERNAME": "your_username"
      }
    }
  }
}
```

No token needed for MCP server either!

---

## 📂 Project Structure

```
openstar-memory/
├── sync_stars.py          # Main sync script (auto-detects repo, token optional)
├── mcp_server.py          # MCP server (no token needed)
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
# YourUsername's GitHub Stars

Last updated: 2026-02-01 23:24:00 UTC

Total stars: 347

## Recently Starred

### [supermemoryai/supermemory](https://github.com/supermemoryai/supermemory)
⭐ 4,521 | 🔤 TypeScript | 📅 Starred: 2026-01-28

Build your own second brain with supermemory...

**Topics:** ai, knowledge-graph, memory

---
```

---

## ❓ FAQ

### Do I need a GitHub token?
**No!** Token is only needed if you want auto-commit mode. Without a token, the script works perfectly fine and generates the markdown locally.

### What are the rate limits?
- **Without token:** 60 requests/hour (enough for ~6000 stars)
- **With token:** 5000 requests/hour

### Can I use this for any GitHub user?
Yes! Just change `GITHUB_USERNAME` to any public GitHub user and run it.

### Why is repo detection automatic?
The script reads your git remote URL and determines where to commit. No manual configuration needed!

---

## 🎯 Use Cases

1. **Quick Reference** - Generate markdown for any GitHub user instantly
2. **Personal Knowledge Base** - Track YOUR stars with auto-commit
3. **Research** - Analyze what repos people in your field star
4. **Portfolio** - Showcase your curated list
5. **MCP Integration** - Semantic search through stars in Claude/Cursor

---

## 🛠️ Advanced

### Use for ANY GitHub User

```bash
# No need to fork! Just set any username
GITHUB_USERNAME=torvalds python sync_stars.py

# Generates: torvalds-starred-repos.md
```

### Multiple Users

```bash
# Generate for multiple users
for user in torvalds gvanrossum dhh; do
  GITHUB_USERNAME=$user python sync_stars.py
done
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
- [GitHub API](https://docs.github.com/en/rest) - Public API

---

**Built with ❤️ for the open source community**
