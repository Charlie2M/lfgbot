import asyncio

import aiohttp

# Anything that can go wrong talking to the API: connection refused, timeout, or a 4xx/5xx response.
API_ERRORS = (aiohttp.ClientError, asyncio.TimeoutError)


class GameStatsClient:
    """Small async wrapper around Game Stats API (github.com/Charlie2M/game-stats-api)."""

    def __init__(self, base_url: str, api_key: str | None):
        self.base_url = base_url.rstrip("/")
        # The API refuses writes without this key. Reads are public, so the bot still works read-only without it.
        headers = {"X-API-Key": api_key} if api_key else {}
        # aiohttp instead of requests: requests would block the event loop and freeze the whole bot
        # while waiting for a response. discord.py already depends on aiohttp.
        self.session = aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=5))

    async def close(self):
        await self.session.close()

    async def get_player_by_discord(self, discord_id: int) -> dict | None:
        async with self.session.get(f"{self.base_url}/players/by-discord/{discord_id}") as response:
            if response.status == 404:
                return None
            response.raise_for_status()
            return await response.json()

    async def create_player(self, username: str, discord_id: int) -> dict:
        payload = {"username": username, "discord_id": str(discord_id)}
        async with self.session.post(f"{self.base_url}/players", json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def set_profile(self, player_id: int, discord_id: int, game: str, rank: str, region: str) -> dict:
        payload = {"rank": rank, "region": region}
        # The API checks this matches the player's linked Discord account, so users can only edit their own profile.
        headers = {"X-Discord-User-Id": str(discord_id)}
        url = f"{self.base_url}/players/{player_id}/profiles/{game}"
        async with self.session.put(url, json=payload, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def search_profiles(self, game: str, region: str | None = None) -> list[dict]:
        params = {"game": game}
        if region:
            params["region"] = region
        async with self.session.get(f"{self.base_url}/profiles", params=params) as response:
            response.raise_for_status()
            return await response.json()
