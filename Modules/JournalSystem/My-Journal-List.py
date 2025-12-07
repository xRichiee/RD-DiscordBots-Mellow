import discord
from discord import app_commands
from discord.ext import commands
import json
from pathlib import Path


BASE_DIR = Path("Data/Journals")


class JournalListCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        BASE_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # /myjournallist
    # ------------------------------------------------------------------
    @app_commands.command(
        name="myjournallist",
        description="View a list of your saved journal entries."
    )
    async def myjournallist(self, interaction: discord.Interaction):

        guild_id = interaction.guild.id if interaction.guild else "DM"
        user_id = interaction.user.id

        guild_folder = BASE_DIR / str(guild_id)
        journal_file = guild_folder / f"{user_id}_journal.json"

        # No journal file
        if not journal_file.exists():
            embed = discord.Embed(
                description="You don't have any journal entries yet.",
                color=discord.Color.blurple()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Load data
        try:
            with journal_file.open("r", encoding="utf-8") as f:
                journal_data = json.load(f)
        except Exception:
            journal_data = []

        # Empty file
        if len(journal_data) == 0:
            embed = discord.Embed(
                description="You don't have any journal entries yet.",
                color=discord.Color.blurple()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Build formatted text
        lines = []
        for entry in journal_data:
            lines.append(
                f"**ID {entry['id']} — {entry['timestamp']}**\n"
                f"{entry['content']}\n"
            )

        embed = discord.Embed(
            title="Your Journal Entries",
            description="\n".join(lines),
            color=discord.Color.blurple()
        )

        embed.set_footer(text="Use /myjournals <id> to view a specific entry.")

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(JournalListCog(bot))
