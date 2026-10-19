# LFGBot

A Discord bot that helps small gaming communities find people to play with. Built with [discord.py](https://github.com/Rapptz/discord.py) using slash commands.

## Features

- `/ping`: quick check that the bot is online and responsive.
- `/lfg <game> [note]`: posts a "looking for group" request and automatically creates a thread so people who want to join can reply without cluttering the main channel. Only works in servers, not DMs.
- `/profile <rank> <region>`: saves your Valorant rank (Iron to Radiant) and region. When you post `/lfg Valorant`, the post shows your rank and region and lists players in this server from the same region within one rank of you (shown as mentions, without pinging them).

## Tech stack

- Python 3
- [discord.py](https://github.com/Rapptz/discord.py) (slash commands via `app_commands`)
- [python-dotenv](https://github.com/theskumar/python-dotenv) for local config
- [aiohttp](https://docs.aiohttp.org/) to call [Game Stats API](https://github.com/Charlie2M/game-stats-api), which stores player profiles

## Setup

1. Clone the repo and install dependencies:

   ```bash
   git clone https://github.com/Charlie2M/lfgbot.git
   cd lfgbot
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. Create a bot application at the [Discord Developer Portal](https://discord.com/developers/applications) and copy its token. No privileged intents are needed.

3. Invite the bot to your server with the `bot` and `applications.commands` scopes and these permissions: Send Messages, Create Public Threads, and Send Messages in Threads.

4. Copy `.env.example` to `.env` and paste in your bot token:

   ```bash
   cp .env.example .env
   ```

   Optional: while developing, set `DEV_GUILD_ID` to your test server's ID (enable Developer Mode in Discord, then right-click the server and choose Copy Server ID). Commands then sync to that server instantly instead of globally.

5. Start [Game Stats API](https://github.com/Charlie2M/game-stats-api) (see its README). The bot expects it at `http://127.0.0.1:8000`; change `GAME_STATS_API_URL` in `.env` if it runs somewhere else. Without it, `/ping` and `/lfg` still work, but `/profile` fails and Valorant posts show no rank info.

   The API only accepts writes from the bot when they carry its shared key. Set `GAME_STATS_API_KEY` in the bot's `.env` to the same value as `BOT_API_KEY` on the API server. Without it, `/lfg` still shows ranks, but `/profile` can't save.

6. Run the bot:

   ```bash
   python bot.py
   ```

## Roadmap

- `v0.4`: rank/server filtering via stored user profiles. Done for Valorant; other games could reuse the same API endpoints.

## Status

Early-stage personal project, actively developed.
