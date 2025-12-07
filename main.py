import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

import discord
from discord.ext import commands
import logging

# --------------------------------------------------------
# Load environment variables
# --------------------------------------------------------
load_dotenv()
TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# --------------------------------------------------------
# Logging Setup
# --------------------------------------------------------
LOG_DIR = Path("Logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "Mellow.log", encoding="utf-8")
    ]
)
log = logging.getLogger("Mellow")

# --------------------------------------------------------
# Discord Bot Setup
# --------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    owner_id=OWNER_ID
)

bot.remove_command("help")

# --------------------------------------------------------
# Auto Load Cogs (ASYNC REQUIRED)
# --------------------------------------------------------
COGS_DIR = Path("Modules")

async def load_cogs():
    for file in COGS_DIR.rglob("*.py"):
        if file.name.startswith("_"):
            continue

        module_path = ".".join(file.with_suffix("").parts)

        try:
            await bot.load_extension(module_path)
            log.info(f"Loaded cog: {module_path}")
        except Exception as e:
            log.error(f"Failed to load {module_path}: {e}")

# --------------------------------------------------------
# Events
# --------------------------------------------------------
@bot.event
async def on_ready():
    log.info(f"Logged in as {bot.user} (ID: {bot.user.id})")

    # ---- Slash Command Sync ----
    try:
        synced = await bot.tree.sync()
        log.info(f"Synced {len(synced)} slash commands globally.")
    except Exception as e:
        log.error(f"Failed to sync commands: {e}")

# --------------------------------------------------------
# Error Handler
# --------------------------------------------------------
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    log.error(f"Error in command '{ctx.command}': {error}")
    await ctx.reply("Something went wrong, sorry 💛", mention_author=False)

# --------------------------------------------------------
# Startup (ASYNC)
# --------------------------------------------------------
if __name__ == "__main__":
    async def main():
        await load_cogs()

        if not TOKEN:
            raise RuntimeError("TOKEN missing from .env")

        await bot.start(TOKEN)

    asyncio.run(main())
