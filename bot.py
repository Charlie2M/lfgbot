import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")

@bot.tree.command(name="ping", description="Check if the bot is responsive")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

@bot.tree.command(name="lfg", description="Post a looking-for-group request")
async def lfg(interaction: discord.Interaction, game: str, note: str = "No additional info"):
    await interaction.response.send_message(
        f"🎮 **{interaction.user.display_name}** is looking for a group!\n"
        f"**Game:** {game}\n"
        f"**Note:** {note}"
    )
    original_response = await interaction.original_response()
    thread = await original_response.create_thread(
        name=f"{game} LFG - {interaction.user.display_name}",
        auto_archive_duration=60
    )
    await thread.send(f"Thread created! React or reply here to join {interaction.user.display_name}'s group.")

bot.run(TOKEN)