# LFGBot

A Discord bot that helps small gaming communities find people to play with. Built with [discord.py](https://github.com/Rapptz/discord.py) using slash commands.

## Features

- `/ping` — quick check that the bot is online and responsive.
- `/lfg <game> [note]` — posts a "looking for group" request and automatically creates a thread so people who want to join can reply without cluttering the main channel.

## Tech stack

- Python 3
- [discord.py](https://github.com/Rapptz/discord.py) (slash commands via `app_commands`)
- [python-dotenv](https://github.com/theskumar/python-dotenv) for local config

## Setup

1. Clone the repo and install dependencies:

   ```bash
   git clone https://github.com/Charlie2M/lfgbot.git
   cd lfgbot
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. Create a bot application at the [Discord Developer Portal](https://discord.com/developers/applications), enable the `Message Content` intent, and copy its token.

3. Copy `.env.example` to `.env` and paste in your bot token:

   ```bash
   cp .env.example .env
   ```

4. Run the bot:

   ```bash
   python bot.py
   ```

## Roadmap

- `v0.4` — rank/server filtering via stored user profiles, so `/lfg` can match players by skill level or game server.

## Status

Early-stage personal project, actively developed.
