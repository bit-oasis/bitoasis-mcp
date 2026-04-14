"""BitOasis MCP Server – exposes BitOasis exchange API as MCP tools."""

from __future__ import annotations

import json
import os

from mcp.server.fastmcp import Context, FastMCP

from bitoasis_mcp.client import BitOasisClient

mcp = FastMCP(
    "BitOasis",
    instructions=(
        "BitOasis MCP server for the BitOasis cryptocurrency exchange. "
        "Use these tools to check market prices, manage orders, view balances, "
        "and handle deposits/withdrawals on BitOasis. "
        "Trading pairs use the format CRYPTO-FIAT (e.g. BTC-AED, ETH-AED, SOL-AED). "
        "Currency symbols are uppercase (BTC, ETH, AED, etc.)."
    ),
    host=os.environ.get("BITOASIS_HOST", "127.0.0.1"),
    port=int(os.environ.get("BITOASIS_PORT", "8000")),
)


def _get_client(ctx: Context | None = None) -> BitOasisClient:
    api_key = None
    # Try request headers first (hosted/HTTP mode)
    if ctx and ctx.request_context and ctx.request_context.request:
        auth = ctx.request_context.request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            api_key = auth[7:]
    # Fall back to env var (local/stdio mode)
    if not api_key:
        api_key = os.environ.get("BITOASIS_API_KEY", "")
    if not api_key:
        raise ValueError(
            "No API key provided. "
            "Pass via Authorization header or BITOASIS_API_KEY env var."
        )
    return BitOasisClient(api_key)


def _fmt(data: dict) -> str:
    return json.dumps(data, indent=2)


# ── Market Data ──────────────────────────────────────────────────────────────


@mcp.tool()
async def get_markets(ctx: Context) -> str:
    """List all available tokens and trading pairs on BitOasis.

    Returns each token's symbol, name, and whether trading/deposits/withdrawals
    are enabled, along with available trading pairs.
    """
    client = _get_client(ctx)
    try:
        return _fmt(await client.get_markets())
    finally:
        await client.close()


@mcp.tool()
async def get_ticker(pair: str, ctx: Context) -> str:
    """Get current price/ticker information for a trading pair.

    Args:
        pair: Trading pair, e.g. "BTC-AED", "ETH-AED", "SOL-AED".
    """
    client = _get_client(ctx)
    try:
        return _fmt(await client.get_ticker(pair))
    finally:
        await client.close()


@mcp.tool()
async def get_order_book(
    pair: str,
    ctx: Context,
    bids_limit: int | None = None,
    asks_limit: int | None = None,
) -> str:
    """Get the order book (bids and asks) for a trading pair.

    Args:
        pair: Trading pair, e.g. "BTC-AED".
        bids_limit: Max number of bid entries to return.
        asks_limit: Max number of ask entries to return.
    """
    client = _get_client(ctx)
    try:
        return _fmt(
            await client.get_order_book(
                pair, bids_limit=bids_limit, asks_limit=asks_limit
            )
        )
    finally:
        await client.close()


@mcp.tool()
async def get_trades(
    pair: str,
    ctx: Context,
    limit: int | None = None,
    from_date: str | None = None,
) -> str:
    """Get recent public trade history for a trading pair.

    Args:
        pair: Trading pair, e.g. "BTC-AED".
        limit: Max number of trades to return.
        from_date: Only return trades from this date onward (YYYY-MM-DD).
    """
    client = _get_client(ctx)
    try:
        return _fmt(await client.get_trades(pair, limit=limit, from_date=from_date))
    finally:
        await client.close()


# ── Account ──────────────────────────────────────────────────────────────────


@mcp.tool()
async def get_balances(ctx: Context) -> str:
    """Get the user's account balances across all currencies.

    Returns a mapping of currency symbol to balance amount.
    """
    client = _get_client(ctx)
    try:
        return _fmt(await client.get_balances())
    finally:
        await client.close()


@mcp.tool()
async def get_banks(ctx: Context) -> str:
    """Get the list of bank accounts the user has registered on BitOasis."""
    client = _get_client(ctx)
    try:
        return _fmt(await client.get_banks())
    finally:
        await client.close()


# ── Orders ───────────────────────────────────────────────────────────────────


@mcp.tool()
async def get_orders(
    pair: str,
    ctx: Context,
    status: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    from_date: str | None = None,
) -> str:
    """List orders for a trading pair, optionally filtered by status.

    Args:
        pair: Trading pair, e.g. "BTC-AED".
        status: Filter by status: "OPEN", "DONE", or "CANCELED".
        offset: Pagination offset.
        limit: Max results (up to 1000).
        from_date: Only return orders from this date (YYYY-MM-DD).
    """
    client = _get_client(ctx)
    try:
        return _fmt(
            await client.get_orders(
                pair, status=status, offset=offset, limit=limit, from_date=from_date
            )
        )
    finally:
        await client.close()


@mcp.tool()
async def get_order(order_id: int, ctx: Context) -> str:
    """Get details of a specific order by ID.

    Args:
        order_id: The order ID.
    """
    client = _get_client(ctx)
    try:
        return _fmt(await client.get_order(order_id))
    finally:
        await client.close()


@mcp.tool()
async def place_order(
    pair: str,
    side: str,
    order_type: str,
    amount: str,
    ctx: Context,
    price: str | None = None,
    stop_price: str | None = None,
    test: bool = False,
) -> str:
    """Place a new order on BitOasis Pro exchange.

    Args:
        pair: Trading pair, e.g. "BTC-AED", "SOL-AED".
        side: "buy" or "sell".
        order_type: "limit", "market", "stop", or "stop_limit".
        amount: Amount of the base currency (as a string).
        price: Limit price (required for "limit" and "stop_limit" orders).
        stop_price: Stop price (required for "stop" and "stop_limit" orders).
        test: If true, validates the order without placing it.
    """
    client = _get_client(ctx)
    try:
        return _fmt(
            await client.place_order(
                pair=pair,
                side=side,
                order_type=order_type,
                amount=amount,
                price=price,
                stop_price=stop_price,
                test=test,
            )
        )
    finally:
        await client.close()


@mcp.tool()
async def cancel_order(order_id: int, ctx: Context) -> str:
    """Cancel an open order.

    Args:
        order_id: The ID of the order to cancel.
    """
    client = _get_client(ctx)
    try:
        return _fmt(await client.cancel_order(order_id))
    finally:
        await client.close()


# ── Coin Deposits ────────────────────────────────────────────────────────────


@mcp.tool()
async def get_coin_deposits(
    currency: str,
    ctx: Context,
    offset: int | None = None,
    limit: int | None = None,
    from_date: str | None = None,
) -> str:
    """Get deposit history for a specific cryptocurrency.

    Args:
        currency: Crypto symbol, e.g. "BTC", "ETH".
        offset: Pagination offset.
        limit: Max results (up to 1000).
        from_date: Only return deposits from this date (YYYY-MM-DD).
    """
    client = _get_client(ctx)
    try:
        return _fmt(
            await client.get_coin_deposits(
                currency, offset=offset, limit=limit, from_date=from_date
            )
        )
    finally:
        await client.close()


@mcp.tool()
async def get_coin_deposit(deposit_id: int, ctx: Context) -> str:
    """Get details of a specific coin deposit.

    Args:
        deposit_id: The deposit ID.
    """
    client = _get_client(ctx)
    try:
        return _fmt(await client.get_coin_deposit(deposit_id))
    finally:
        await client.close()


@mcp.tool()
async def new_coin_deposit_address(
    currency: str,
    ctx: Context,
    network: str | None = None,
) -> str:
    """Generate a new deposit address for a cryptocurrency.

    Args:
        currency: Crypto symbol, e.g. "BTC", "ETH".
        network: Network code (e.g. "bitcoin", "erc20", "trc20"). Uses default if omitted.
    """
    client = _get_client(ctx)
    try:
        return _fmt(await client.new_coin_deposit_address(currency, network=network))
    finally:
        await client.close()


# ── Coin Withdrawals ─────────────────────────────────────────────────────────


@mcp.tool()
async def get_coin_withdrawals(
    currency: str,
    ctx: Context,
    offset: int | None = None,
    limit: int | None = None,
    from_date: str | None = None,
) -> str:
    """Get withdrawal history for a specific cryptocurrency.

    Args:
        currency: Crypto symbol, e.g. "BTC", "ETH".
        offset: Pagination offset.
        limit: Max results (up to 1000).
        from_date: Only return withdrawals from this date (YYYY-MM-DD).
    """
    client = _get_client(ctx)
    try:
        return _fmt(
            await client.get_coin_withdrawals(
                currency, offset=offset, limit=limit, from_date=from_date
            )
        )
    finally:
        await client.close()


@mcp.tool()
async def get_coin_withdrawal(withdrawal_id: int, ctx: Context) -> str:
    """Get details of a specific coin withdrawal.

    Args:
        withdrawal_id: The withdrawal ID.
    """
    client = _get_client(ctx)
    try:
        return _fmt(await client.get_coin_withdrawal(withdrawal_id))
    finally:
        await client.close()


@mcp.tool()
async def new_coin_withdrawal(
    currency: str,
    amount: str,
    withdrawal_address: str,
    ctx: Context,
    withdrawal_address_id: str | None = None,
    network: str | None = None,
) -> str:
    """Create a new cryptocurrency withdrawal.

    Note: BitOasis requires email and SMS/TOTP confirmation for withdrawals.

    Args:
        currency: Crypto symbol, e.g. "BTC", "ETH".
        amount: Amount to withdraw (as string).
        withdrawal_address: Destination wallet address.
        withdrawal_address_id: Additional address identifier (e.g. XRP tag, XLM memo).
        network: Network code (e.g. "bitcoin", "erc20"). Uses default if omitted.
    """
    client = _get_client(ctx)
    try:
        return _fmt(
            await client.new_coin_withdrawal(
                currency=currency,
                amount=amount,
                withdrawal_address=withdrawal_address,
                withdrawal_address_id=withdrawal_address_id,
                network=network,
            )
        )
    finally:
        await client.close()


@mcp.tool()
async def get_coin_withdrawal_fees(ctx: Context) -> str:
    """Get withdrawal fees for all supported cryptocurrencies."""
    client = _get_client(ctx)
    try:
        return _fmt(await client.get_coin_withdrawal_fees())
    finally:
        await client.close()


# ── Fiat Deposits ────────────────────────────────────────────────────────────


@mcp.tool()
async def get_fiat_deposits(
    ctx: Context,
    offset: int | None = None,
    limit: int | None = None,
    from_date: str | None = None,
) -> str:
    """Get fiat (AED) deposit history.

    Args:
        offset: Pagination offset.
        limit: Max results (up to 1000).
        from_date: Only return deposits from this date (YYYY-MM-DD).
    """
    client = _get_client(ctx)
    try:
        return _fmt(
            await client.get_fiat_deposits(
                offset=offset, limit=limit, from_date=from_date
            )
        )
    finally:
        await client.close()


@mcp.tool()
async def get_fiat_deposit(deposit_id: int, ctx: Context) -> str:
    """Get details of a specific fiat deposit.

    Args:
        deposit_id: The deposit ID.
    """
    client = _get_client(ctx)
    try:
        return _fmt(await client.get_fiat_deposit(deposit_id))
    finally:
        await client.close()


# ── Fiat Withdrawals ─────────────────────────────────────────────────────────


@mcp.tool()
async def get_fiat_withdrawals(
    ctx: Context,
    offset: int | None = None,
    limit: int | None = None,
    from_date: str | None = None,
) -> str:
    """Get fiat (AED) withdrawal history.

    Args:
        offset: Pagination offset.
        limit: Max results (up to 1000).
        from_date: Only return withdrawals from this date (YYYY-MM-DD).
    """
    client = _get_client(ctx)
    try:
        return _fmt(
            await client.get_fiat_withdrawals(
                offset=offset, limit=limit, from_date=from_date
            )
        )
    finally:
        await client.close()


@mcp.tool()
async def get_fiat_withdrawal(withdrawal_id: int, ctx: Context) -> str:
    """Get details of a specific fiat withdrawal.

    Args:
        withdrawal_id: The withdrawal ID.
    """
    client = _get_client(ctx)
    try:
        return _fmt(await client.get_fiat_withdrawal(withdrawal_id))
    finally:
        await client.close()


@mcp.tool()
async def new_fiat_withdrawal(
    amount: str,
    ctx: Context,
    currency: str = "AED",
    origin: str | None = None,
) -> str:
    """Create a new fiat withdrawal to a registered bank account.

    Args:
        amount: Amount to withdraw.
        currency: Fiat currency (default: "AED").
        origin: Origin identifier.
    """
    client = _get_client(ctx)
    try:
        return _fmt(
            await client.new_fiat_withdrawal(
                amount=amount, currency=currency, origin=origin
            )
        )
    finally:
        await client.close()


@mcp.tool()
async def cancel_fiat_withdrawal(withdrawal_id: int, ctx: Context) -> str:
    """Cancel a pending fiat withdrawal.

    Args:
        withdrawal_id: The withdrawal ID to cancel.
    """
    client = _get_client(ctx)
    try:
        return _fmt(await client.cancel_fiat_withdrawal(withdrawal_id))
    finally:
        await client.close()


def main() -> None:
    transport = os.environ.get("BITOASIS_TRANSPORT", "stdio")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
