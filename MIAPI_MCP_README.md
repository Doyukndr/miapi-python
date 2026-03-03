# MIAPI MCP Server

Connect AI assistants to real-time web search. Get grounded answers with citations through Claude Desktop, Cursor, Windsurf, and any MCP-compatible client.

## Quick Start

### 1. Install

```bash
pip install "mcp[cli]" httpx
```

### 2. Set your API key

Get a free key at [miapi.uk/signup.html](https://miapi.uk/signup.html)

```bash
export MIAPI_API_KEY="your_api_key_here"
```

### 3. Run

```bash
python miapi_mcp_server.py
```

## Connect to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "miapi": {
      "command": "python",
      "args": ["/path/to/miapi_mcp_server.py"],
      "env": {
        "MIAPI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Connect to Cursor

Go to **Settings > MCP Servers > Add**, then:

```json
{
  "command": "python",
  "args": ["/path/to/miapi_mcp_server.py"],
  "env": {
    "MIAPI_API_KEY": "your_api_key_here"
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `web_answer` | Get AI-synthesized answers with inline citations |
| `web_search` | Raw web search results (titles, URLs, snippets) |
| `news_search` | Search recent news articles |
| `image_search` | Search for images |
| `check_usage` | Check your query balance and usage |

## Examples

Once connected, just ask your AI assistant things like:

- "Search the web for the latest SpaceX launch"
- "What is the current price of Bitcoin?" 
- "Find recent news about AI regulations"
- "Check my MIAPI usage"

The assistant will automatically use MIAPI's tools to search the web and provide sourced answers.

## Pricing

- **Free**: 500 queries/month
- **Starter**: $9 for 2,500 queries
- **Developer**: $33 for 10,000 queries  
- **Pro**: $90 for 30,000 queries
- **Scale**: $250 for 100,000 queries

All purchases are one-time. No subscriptions. Never expires.

## Links

- Website: [miapi.uk](https://miapi.uk)
- API Docs: [api.miapi.uk](https://api.miapi.uk)
- Python SDK: `pip install miapi-sdk`
- GitHub: [github.com/Doyukndr/miapi-python](https://github.com/Doyukndr/miapi-python)
