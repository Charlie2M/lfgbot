import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os

from game_stats import API_ERRORS, GameStatsClient

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
# Optional: set this to a server ID while developing so commands sync there instantly.
DEV_GUILD_ID = os.getenv("DEV_GUILD_ID")
GAME_STATS_API_URL = os.getenv("GAME_STATS_API_URL", "http://127.0.0.1:8000")

if not TOKEN:
    raise SystemExit("DISCORD_TOKEN is not set. Copy .env.example to .env and add your bot token.")

VALORANT = "Valorant"
# Lowest to highest, so a rank's position in the list is its skill level.
VALORANT_RANKS = ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ascendant", "Immortal", "Radiant"]
VALORANT_REGIONS = {
    "NA": "North America",
    "LATAM": "Latin America",
    "BR": "Brazil",
    "EU": "Europe",
    "AP": "Asia Pacific",
    "KR": "Korea",
}


class LFGBot(commands.Bot):
    stats: GameStatsClient | None = None

    async def setup_hook(self):
        # setup_hook runs once before connecting, unlike on_ready which can fire again on reconnects.
        self.stats = GameStatsClient(GAME_STATS_API_URL)

        if DEV_GUILD_ID:
            guild = discord.Object(id=int(DEV_GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} command(s) to dev guild {DEV_GUILD_ID}")
        else:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s) globally")

    async def close(self):
        # stats is still None if login failed before setup_hook ran.
        if self.stats:
            await self.stats.close()
        await super().close()


# commands.Bot requires a prefix. Mentioning the bot is the only prefix that works without the
# Message Content intent, and there are no prefix commands anyway.
bot = LFGBot(command_prefix=commands.when_mentioned, intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="ping", description="Check if the bot is responsive")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

@bot.tree.command(name="profile", description="Set your Valorant rank and region so /lfg can match you")
@app_commands.choices(
    rank=[app_commands.Choice(name=rank, value=rank) for rank in VALORANT_RANKS],
    region=[app_commands.Choice(name=f"{name} ({code})", value=code) for code, name in VALORANT_REGIONS.items()],
)
async def profile(interaction: discord.Interaction, rank: app_commands.Choice[str], region: app_commands.Choice[str]):
    # Discord only waits 3 seconds for a response, so acknowledge first, then call the API.
    await interaction.response.defer(ephemeral=True)
    try:
        player = await bot.stats.get_player_by_discord(interaction.user.id)
        if player is None:
            player = await bot.stats.create_player(interaction.user.name, interaction.user.id)
        await bot.stats.set_profile(player["id"], VALORANT, rank.value, region.value)
    except API_ERRORS as error:
        print(f"Game Stats API error in /profile: {error!r}")
        await interaction.followup.send("I couldn't save your profile right now. Try again later.", ephemeral=True)
        return
    await interaction.followup.send(f"Saved your Valorant profile: {rank.value}, {region.value}.", ephemeral=True)


async def valorant_details(interaction: discord.Interaction) -> str:
    """Extra lines for a Valorant /lfg post: the poster's rank and region, and players near their rank."""
    try:
        player = await bot.stats.get_player_by_discord(interaction.user.id)
        profiles = player["profiles"] if player else []
        mine = next((p for p in profiles if p["game"] == VALORANT), None)
        if mine is None or mine["rank"] not in VALORANT_RANKS:
            return "\n*Set your rank and region with `/profile` to see players near your rank.*"

        same_region = await bot.stats.search_profiles(VALORANT, region=mine["region"])
        my_level = VALORANT_RANKS.index(mine["rank"])
        nearby_ids = [
            int(p["discord_id"]) for p in same_region
            if p["discord_id"] and p["discord_id"] != str(interaction.user.id)
            and p["rank"] in VALORANT_RANKS
            and abs(VALORANT_RANKS.index(p["rank"]) - my_level) <= 1
        ][:100]  # Discord's limit for one member lookup

        # Profiles are shared across every server the bot is in, so only list people in this one.
        # Looking members up by ID works without the privileged Members intent.
        members = await interaction.guild.query_members(user_ids=nearby_ids, limit=len(nearby_ids)) if nearby_ids else []
    except API_ERRORS as error:
        print(f"Game Stats API error in /lfg: {error!r}")
        return ""

    lines = f"\n**Rank:** {mine['rank']} | **Region:** {mine['region']}"
    if members:
        lines += "\n**Players near your rank here:** " + ", ".join(m.mention for m in members[:10])
    return lines


@bot.tree.command(name="lfg", description="Post a looking-for-group request")
@app_commands.guild_only()
async def lfg(interaction: discord.Interaction, game: str, note: str = "No additional info"):
    await interaction.response.defer(thinking=True)

    details = ""
    if game.strip().lower() == VALORANT.lower():
        details = await valorant_details(interaction)

    original_response = await interaction.edit_original_response(
        content=(
            f"🎮 **{interaction.user.display_name}** is looking for a group!\n"
            f"**Game:** {game}\n"
            f"**Note:** {note}"
            f"{details}"
        ),
        # game and note are user input, so don't let them ping @everyone or roles. This also means
        # nearby players are shown as mentions without being notified.
        allowed_mentions=discord.AllowedMentions.none(),
    )
    try:
        thread = await original_response.create_thread(
            name=f"{game} LFG - {interaction.user.display_name}"[:100],  # Discord's thread name limit
            auto_archive_duration=60
        )
        await thread.send(f"Thread created! React or reply here to join {interaction.user.display_name}'s group.")
    except discord.Forbidden:
        await interaction.followup.send(
            "I couldn't create a thread here. I need the Create Public Threads and "
            "Send Messages in Threads permissions in this channel.",
            ephemeral=True,
        )
    except discord.HTTPException:
        await interaction.followup.send(
            "I couldn't create a thread here (for example, threads can't be made inside another thread).",
            ephemeral=True,
        )

bot.run(TOKEN)
