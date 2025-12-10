import discord
from discord import app_commands
from discord.ext import commands
import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path("Data/Journals")


class JournalCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        BASE_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # /journal <content>
    # ------------------------------------------------------------------
    @app_commands.command(
        name="journal",
        description="Privately write a journal entry."
    )
    @app_commands.describe(content="Your private journal entry")
    async def journal(self, interaction: discord.Interaction, content: str):

        guild_id = interaction.guild.id if interaction.guild else "DM"
        user_id = interaction.user.id

        # folder for this server
        guild_folder = BASE_DIR / str(guild_id)
        guild_folder.mkdir(parents=True, exist_ok=True)

        # file for this user
        journal_file = guild_folder / f"{user_id}_journal.json"

        # load previous entries
        if journal_file.exists():
            try:
                with journal_file.open("r", encoding="utf-8") as f:
                    journal_data = json.load(f)
            except Exception:
                journal_data = []
        else:
            journal_data = []

        # Determine next ID
        next_id = 1 if len(journal_data) == 0 else max(entry["id"] for entry in journal_data) + 1

        # Create new journal entry
        entry = {
            "id": next_id,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "content": content
        }

        journal_data.append(entry)

        # Save updated journal
        with journal_file.open("w", encoding="utf-8") as f:
            json.dump(journal_data, f, indent=4)

        # ------------------------------------------------------------
        # Embed Response
        # ------------------------------------------------------------
        embed = discord.Embed(
            description=(
                f"Your journal entry has been saved (ID **{next_id}**). 💛\n\n"
                f"You can view your journals using:\n"
                f"• `/myjournallist`\n"
                f"• `/myjournals <id>` if you know a specific entry ID"
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(JournalCog(bot))
