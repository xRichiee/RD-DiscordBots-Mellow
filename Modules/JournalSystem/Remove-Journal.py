import discord
from discord import app_commands
from discord.ext import commands
import json
from pathlib import Path


BASE_DIR = Path("Data/Journals")


class RemoveJournalCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------------------------------------------
    # AUTOCOMPLETE: list journal IDs
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
            except:
                journal_data = []
        else:
            journal_data = []

        for entry in journal_data:
            entry_id = str(entry["id"])
            if current in entry_id:
                choices.append(app_commands.Choice(name=f"ID {entry_id}", value=entry_id))

        return choices[:25]

    # ------------------------------------------------------------
    # /removejournal <id>
    # ------------------------------------------------------------
    @app_commands.command(
        name="removejournal",
        description="Delete one of your journal entries."
    )
    @app_commands.describe(entry_id="The journal ID you want to delete.")
    @app_commands.autocomplete(entry_id=journal_id_autocomplete)
    async def removejournal(self, interaction: discord.Interaction, entry_id: str):

        guild_id = interaction.guild.id if interaction.guild else "DM"
        user_id = interaction.user.id
        entry_id = int(entry_id)

        journal_file = BASE_DIR / str(guild_id) / f"{user_id}_journal.json"

        # If no file exists
        if not journal_file.exists():
            embed = discord.Embed(
                description="You don't have any journal entries to remove.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Load entries
        try:
            with journal_file.open("r", encoding="utf-8") as f:
                journal_data = json.load(f)
        except:
            journal_data = []

        # Find entry
        before_count = len(journal_data)
        journal_data = [e for e in journal_data if e["id"] != entry_id]
        after_count = len(journal_data)

        if before_count == after_count:
            embed = discord.Embed(
                description=f"No journal entry with ID **{entry_id}** was found.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Save the reduced list
        with journal_file.open("w", encoding="utf-8") as f:
            json.dump(journal_data, f, indent=4)

        embed = discord.Embed(
            description=f"Your journal entry (ID **{entry_id}**) has been removed.",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(RemoveJournalCog(bot))
