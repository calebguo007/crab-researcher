# CrabRes MCP Server

AI Growth Strategy Agent — use from Claude, ChatGPT, Cursor, or any MCP-compatible client.

## Tools

### `analyze_growth`
Full growth analysis for any product. Researches competitors, finds target users, and suggests personalized strategies.

```json
{
  "product_description": "AI resume optimizer for job seekers",
  "budget": "$100/month"
}
```

### `find_competitors`
Find and analyze competitors with real data (pricing, features, traffic).

```json
{
  "product_or_niche": "website blocker for remote workers"
}
```

### `find_target_users`
Discover where your target users are discussing their problems right now.

```json
{
  "product_description": "AI writing assistant for bloggers"
}
```

## Setup

### For Claude Code / Cursor
Add to your MCP settings:

```json
{
  "mcpServers": {
    "crabres": {
      "url": "https://crab-researcher.onrender.com/api/mcp"
    }
  }
}
```

### Direct API
```bash
curl -X POST https://crab-researcher.onrender.com/api/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"find_competitors","arguments":{"product_or_niche":"AI writing tool"}}}'
```

## About

CrabRes is an AI growth strategy agent with 13 specialized experts. 
Unlike generic AI, it researches your specific market with real data.

Learn more: https://crabres.com
