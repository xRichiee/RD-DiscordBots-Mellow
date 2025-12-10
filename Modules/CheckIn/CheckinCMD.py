import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from datetime import datetime

class DailyCheckIn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.moods = [
            "😊 Happy",
            "😟 Stressed",
            "😔 Sad",
            "😐 Neutral",
            "🔥 Motivated"
        ]

        self.base_path = "Data/CheckIns"


    # --------------- INTERNAL HELPERS -----------------

    def get_user_file(self, guild_id: int, user_id: int):
        folder = os.path.join(self.base_path, str(guild_id))
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, f"{user_id}.json")

    def load_history(self, guild_id: int, user_id: int):
        """Loads the user's existing check-in log or returns empty list."""
        file_path = self.get_user_file(guild_id, user_id)

        if not os.path.exists(file_path):
            return []

        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except:
            return []  # if corrupted, reset

    def has_checked_in_today(self, history):
        """Returns True if there's already a check-in entry for today."""
        today = datetime.now().strftime("%Y-%m-%d")
        for entry in history:
            if entry.get("date") == today:
                return True
        return False

    def save_checkin(self, guild_id: int, user_id: int, mood: str):
        """Appends a new daily check-in entry."""
        file_path = self.get_user_file(guild_id, user_id)
        history = self.load_history(guild_id, user_id)

        today = datetime.now().strftime("%Y-%m-%d")

        history.append({
            "date": today,
            "mood": mood
        })

        with open(file_path, "w") as f:
            json.dump(history, f, indent=4)

    # ---------------------------------------------------


    @app_commands.command(
        name="dailycheckin",
        description="Log your daily mood check-in."
    )
    @app_commands.describe(
        mood="Select the mood that best describes how you're feeling today."
    )
    @app_commands.choices(
        mood=[
            app_commands.Choice(name="😊 Happy", value="happy"),
            app_commands.Choice(name="😟 Stressed", value="stressed"),
            app_commands.Choice(name="😔 Sad", value="sad"),
            app_commands.Choice(name="😐 Neutral", value="neutral"),
            app_commands.Choice(name="🔥 Motivated", value="motivated"),
        ]
    )
    async def dailycheckin(self, interaction: discord.Interaction, mood: app_commands.Choice[str]):

        guild_id = interaction.guild.id
        user_id = interaction.user.id

        # Load history and ensure only ONE check-in per day
        history = self.load_history(guild_id, user_id)
        if self.has_checked_in_today(history):
            embed = discord.Embed(
                title="🧠 Daily Check-In Already Logged",
                description="You’ve already checked in today.\n\nThank you for staying consistent — try again tomorrow. 💙",
                color=0xffc857
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Store their check-in as a new entry
        self.save_checkin(guild_id, user_id, mood.value)

        embed = discord.Embed(
            title="🧠 Daily Check-In Logged",
            description=f"**Mood:** {mood.name}",
            color=0x4c9aff
        )

        embed.set_footer(text="Thank you for checking in. You’re doing great. 💙")

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(DailyCheckIn(bot))
