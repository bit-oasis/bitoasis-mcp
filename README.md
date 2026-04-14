# BitOasis MCP Server

An MCP (Model Context Protocol) server that exposes the [BitOasis](https://bitoasis.net) cryptocurrency exchange API as tools for AI assistants.

## Quick Start

### Prerequisites

- A verified BitOasis account with an API token (generate one at **Settings > [API Token Management](https://bitoasis.net/en/settings/tokens)**)

### Install via uvx (recommended)

Add to your MCP client config (Claude Desktop, VS Code, Cursor, etc.):

```json
{
  "mcpServers": {
    "bitoasis": {
      "command": "uvx",
      "args": ["bitoasis-mcp"],
      "env": {
        "BITOASIS_API_KEY": "your-api-token-here"
      }
    }
  }
}
```

That's it — restart your MCP client and you're ready to go.

### Install via Docker

```json
{
  "mcpServers": {
    "bitoasis": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "BITOASIS_API_KEY", "bitoasis-mcp"],
      "env": {
        "BITOASIS_API_KEY": "your-api-token-here"
      }
    }
  }
}
```

## Available Tools

### Market Data
- **get_markets** — List all tokens and trading pairs
- **get_ticker** — Current price for a pair (e.g. `BTC-AED`)
- **get_order_book** — Bids and asks for a pair
- **get_trades** — Recent public trade history

### Account
- **get_balances** — Your balances across all currencies
- **get_banks** — Your registered bank accounts

### Orders
- **get_orders** — List orders for a pair (filter by OPEN/DONE/CANCELED)
- **get_order** — Order details by ID
- **place_order** — Place a limit, market, stop, or stop_limit order
- **cancel_order** — Cancel an open order

### Deposits
- **get_coin_deposits** / **get_coin_deposit** — Crypto deposit history/details
- **new_coin_deposit_address** — Generate a deposit address
- **get_fiat_deposits** / **get_fiat_deposit** — Fiat deposit history/details

### Withdrawals
- **get_coin_withdrawals** / **get_coin_withdrawal** — Crypto withdrawal history/details
- **new_coin_withdrawal** — Withdraw crypto to an external address
- **get_coin_withdrawal_fees** — Withdrawal fees per currency
- **get_fiat_withdrawals** / **get_fiat_withdrawal** — Fiat withdrawal history/details
- **new_fiat_withdrawal** — Withdraw fiat to a registered bank
- **cancel_fiat_withdrawal** — Cancel a pending fiat withdrawal

## Example Prompts

> "What's the current price of BTC-AED?"

> "Show my open orders for ETH-AED"

> "Place a SOL-AED limit buy order: 2 SOL at 1000 AED"

> "What are my balances?"

## Development

```bash
git clone https://github.com/bit-oasis/bitoasis-mcp.git
cd bitoasis-mcp
uv sync
```

Run from source:

```json
{
  "mcpServers": {
    "bitoasis": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/bitoasis-mcp", "bitoasis-mcp"],
      "env": {
        "BITOASIS_API_KEY": "your-api-token-here"
      }
    }
  }
}
```

## License

MIT
