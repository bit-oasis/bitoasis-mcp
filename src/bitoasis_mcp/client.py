"""HTTP client for the BitOasis API (https://api.bitoasis.net/v1/)."""

from __future__ import annotations

from typing import Any

import httpx

BASE_URL = "https://api.bitoasis.net/v1"


class BitOasisClient:
    """Thin wrapper around the BitOasis REST API."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=BASE_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        resp = await self._client.request(method, path, params=params, json=json_body)
        resp.raise_for_status()
        return resp.json()

    # --- Market Data (public) ---

    async def get_markets(self) -> dict[str, Any]:
        return await self._request("GET", "/exchange/markets")

    async def get_ticker(self, pair: str) -> dict[str, Any]:
        return await self._request("GET", f"/exchange/ticker/{pair}")

    async def get_order_book(
        self,
        pair: str,
        *,
        bids_limit: int | None = None,
        asks_limit: int | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if bids_limit is not None:
            params["bids_limit"] = bids_limit
        if asks_limit is not None:
            params["asks_limit"] = asks_limit
        return await self._request(
            "GET", f"/exchange/order-book/{pair}", params=params or None
        )

    async def get_trades(
        self,
        pair: str,
        *,
        limit: int | None = None,
        from_date: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if from_date is not None:
            params["from_date"] = from_date
        return await self._request(
            "GET", f"/exchange/trades/{pair}", params=params or None
        )

    # --- Accounts ---

    async def get_balances(self) -> dict[str, Any]:
        return await self._request("GET", "/exchange/balances")

    # --- Banks ---

    async def get_banks(self) -> dict[str, Any]:
        return await self._request("GET", "/exchange/banks")

    # --- Orders ---

    async def get_orders(
        self,
        pair: str,
        *,
        status: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        from_date: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if from_date is not None:
            params["from_date"] = from_date
        return await self._request(
            "GET", f"/exchange/orders/{pair}", params=params or None
        )

    async def get_order(self, order_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/exchange/order/{order_id}")

    async def place_order(
        self,
        *,
        pair: str,
        side: str,
        order_type: str,
        amount: str,
        price: str | None = None,
        stop_price: str | None = None,
        test: bool = False,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "pair": pair,
            "side": side,
            "type": order_type,
            "amount": amount,
        }
        if price is not None:
            body["price"] = price
        if stop_price is not None:
            body["stop_price"] = stop_price
        params = {"test": "true"} if test else None
        return await self._request(
            "POST", "/exchange/order", json_body=body, params=params
        )

    async def cancel_order(self, order_id: int) -> dict[str, Any]:
        return await self._request(
            "POST", "/exchange/cancel-order", json_body={"id": order_id}
        )

    # --- Coin Deposits ---

    async def get_coin_deposits(
        self,
        currency: str,
        *,
        offset: int | None = None,
        limit: int | None = None,
        from_date: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if from_date is not None:
            params["from_date"] = from_date
        return await self._request(
            "GET", f"/exchange/coin-deposits/{currency}", params=params or None
        )

    async def get_coin_deposit(self, deposit_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/exchange/coin-deposit/{deposit_id}")

    async def new_coin_deposit_address(
        self,
        currency: str,
        *,
        network: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"currency": currency}
        if network is not None:
            body["network"] = network
        return await self._request("POST", "/exchange/coin-deposit", json_body=body)

    # --- Coin Withdrawals ---

    async def get_coin_withdrawals(
        self,
        currency: str,
        *,
        offset: int | None = None,
        limit: int | None = None,
        from_date: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if from_date is not None:
            params["from_date"] = from_date
        return await self._request(
            "GET", f"/exchange/coin-withdrawals/{currency}", params=params or None
        )

    async def get_coin_withdrawal(self, withdrawal_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/exchange/coin-withdrawal/{withdrawal_id}")

    async def new_coin_withdrawal(
        self,
        *,
        currency: str,
        amount: str,
        withdrawal_address: str,
        withdrawal_address_id: str | None = None,
        network: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "currency": currency,
            "amount": amount,
            "withdrawal_address": withdrawal_address,
        }
        if withdrawal_address_id is not None:
            body["withdrawal_address_id"] = withdrawal_address_id
        if network is not None:
            body["network"] = network
        return await self._request("POST", "/exchange/coin-withdrawal", json_body=body)

    async def get_coin_withdrawal_fees(self) -> dict[str, Any]:
        return await self._request("GET", "/exchange/coin-withdrawal-fees")

    # --- Fiat Deposits ---

    async def get_fiat_deposits(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        from_date: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if from_date is not None:
            params["from_date"] = from_date
        return await self._request(
            "GET", "/exchange/fiat-deposits", params=params or None
        )

    async def get_fiat_deposit(self, deposit_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/exchange/fiat-deposit/{deposit_id}")

    # --- Fiat Withdrawals ---

    async def get_fiat_withdrawals(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        from_date: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if from_date is not None:
            params["from_date"] = from_date
        return await self._request(
            "GET", "/exchange/fiat-withdrawals", params=params or None
        )

    async def get_fiat_withdrawal(self, withdrawal_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/exchange/fiat-withdrawal/{withdrawal_id}")

    async def new_fiat_withdrawal(
        self,
        *,
        amount: str,
        currency: str,
        origin: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "amount": {"value": amount, "currency": currency},
        }
        if origin is not None:
            body["origin"] = origin
        return await self._request("POST", "/exchange/fiat-withdrawal", json_body=body)

    async def cancel_fiat_withdrawal(self, withdrawal_id: int) -> dict[str, Any]:
        return await self._request(
            "DELETE", f"/exchange/fiat-withdrawal/{withdrawal_id}"
        )
