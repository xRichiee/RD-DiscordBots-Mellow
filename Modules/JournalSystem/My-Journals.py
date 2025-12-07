import discord
from discord import app_commands
from discord.ext import commands
import json
from pathlib import Path


BASE_DIR = Path("Data/Journals")


class JournalViewCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------------------------------------------
    # AUTOCOMPLETE: Suggest the user's journal IDs
    # ------------------------------------------------------------
    async def journal_id_autocomplete(self, interaction: discord.Interaction, current: str):
        guild_id = interaction.guild.id if interaction.guild else "DM"
        user_id = interaction.user.id

        journal_file = BASE_DIR / str(guild_id) / f"{user_id}_journal.json"

        choices = []

        if journal_file.exists():
            try:
                with journal_file.open("r", encoding="utf-8") as f:
                    journal_data = json.load(f)
            except Exception:
                journal_data = []
        else:
            journal_data = []

        # Filter by typing (optional)
        for entry in journal_data:
            entry_id = str(entry["id"])
            if current in entry_id:
                choices.append(
                    app_commands.Choice(name=f"ID {entry_id}", value=entry_id)
                )

        return choices[:25]  # Discord limit

    # ------------------------------------------------------------
    # /myjournals <id>
    # ------------------------------------------------------------
    @app_commands.command(
        name="myjournals",
        description="View a specific journal entry by ID."
    )
    @app_commands.describe(entry_id="The ID of the journal entry you want to view.")
    @app_commands.autocomplete(entry_id=journal_id_autocomplete)
    async def myjournals(self, interaction: discord.Interaction, entry_id: str):

        guild_id = interaction.guild.id if interaction.guild else "DM"
        user_id = interaction.user.id
        entry_id = int(entry_id)

        journal_file = BASE_DIR / str(guild_id) / f"{user_id}_journal.json"

        if not journal_file.exists():
            embed = discord.Embed(
                description="You don't have any journal entries yet.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Load entries
        try:
            with journal_file.open("r", encoding="utf-8") as f:
                journal_data = json.load(f)
        except Exception:
            journal_data = []

        # Find entry
        entry = next((e for e in journal_data if e["id"] == entry_id), None)

        if not entry:
            embed = discord.Embed(
                description=f"No journal entry with ID **{entry_id}** was found.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Build embed
        embed = discord.Embed(
            title=f"Journal Entry #{entry_id}",
            description=entry["content"],
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"Created at {entry['timestamp']}")

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(JournalViewCog(bot))
