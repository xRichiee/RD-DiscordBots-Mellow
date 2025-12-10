import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from datetime import datetime, timedelta
import io


class CheckInHistory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_path = "Data/CheckIns"

    # --------------- INTERNAL HELPERS -----------------

    def get_user_file(self, guild_id: int, user_id: int):
        folder = os.path.join(self.base_path, str(guild_id))
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
            return []

    def filter_history_by_days(self, history, days: int):
        """Return history entries within the last <days> days (inclusive)."""
        if not history:
            return []

        today = datetime.now().date()
        cutoff = today - timedelta(days=days - 1)

        filtered = []
        for entry in history:
            date_str = entry.get("date")
            mood = entry.get("mood", "unknown")

            try:
                entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except Exception:
                continue

            if entry_date >= cutoff:
                filtered.append({
                    "date": entry_date,
                    "mood": mood
                })

        # sort ascending by date
        filtered.sort(key=lambda x: x["date"])
        return filtered

    def format_history_text(self, entries, days: int, user: discord.User | discord.Member):
        """Builds a plain text representation of the history."""
        lines = []
        lines.append(f"Daily Check-In History for {user} (last {days} day(s))")
        lines.append("-" * 40)

        if not entries:
            lines.append("No check-ins found in this time range.")
        else:
            for entry in entries:
                date_str = entry["date"].strftime("%Y-%m-%d")
                mood = str(entry["mood"]).capitalize()
                lines.append(f"{date_str}: {mood}")

        return "\n".join(lines)

    # ---------------------------------------------------

    @app_commands.command(
        name="checkinhistory",
        description="View your daily check-in history over the past number of days."
    )
    @app_commands.describe(
        days="Number of days to look back (max 30)."
    )
    async def checkinhistory(self, interaction: discord.Interaction, days: app_commands.Range[int, 1, 30]):
        # Ensure used in a server (since we key by guild id)
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True
            )
            return

        guild_id = interaction.guild.id
        user = interaction.user
        user_id = user.id

        history = self.load_history(guild_id, user_id)
        filtered = self.filter_history_by_days(history, days)

        history_text = self.format_history_text(filtered, days, user)

        # If small enough, send as an embed
        if len(history_text) <= 3500:
            # Build embed description without the first line (title line), use as embed title instead
            lines = history_text.split("\n")
            title = lines[0] if lines else "Daily Check-In History"
            desc = "\n".join(lines[2:]) if len(lines) > 2 else "No check-ins found in this time range."

            embed = discord.Embed(
                title=title,
                description=desc,
                color=0x4c9aff
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Too long for embed, return as a text file
        file_buffer = io.BytesIO(history_text.encode("utf-8"))
        discord_file = discord.File(file_buffer, filename="checkin_history.txt")

        await interaction.response.send_message(
            content="Your check-in history is a bit long, so here it is as a file:",
            file=discord_file,
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(CheckInHistory(bot))
