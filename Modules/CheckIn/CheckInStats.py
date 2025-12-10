import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from datetime import datetime, timedelta
import io


class CheckInStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_path = "Data/CheckIns"

        # Map stored mood keys -> pretty labels
        self.mood_labels = {
            "happy": "😊 Happy",
            "stressed": "😟 Stressed",
            "sad": "😔 Sad",
            "neutral": "😐 Neutral",
            "motivated": "🔥 Motivated"
        }

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

        return filtered

    def compute_stats(self, filtered_entries):
        """Count moods across filtered entries."""
        counts = {key: 0 for key in self.mood_labels.keys()}
        total = 0

        for entry in filtered_entries:
            mood_key = str(entry.get("mood", "unknown")).lower()
            if mood_key in counts:
                counts[mood_key] += 1
                total += 1

        return counts, total

    def build_bar(self, value: int, max_value: int, width: int = 10):
        """Simple text bar for visuals."""
        if max_value <= 0:
            return ""
        filled = int((value / max_value) * width)
        filled = max(0, min(width, filled))
        return "█" * filled + "░" * (width - filled)

    def format_stats_text(self, user: discord.User | discord.Member, days: int, counts: dict, total: int):
        """Plain text representation of the stats, for file fallback."""
        lines = []
        lines.append(f"Daily Check-In Stats for {user} (last {days} day(s))")
        lines.append("-" * 40)

        if total == 0:
            lines.append("No check-ins found in this time range.")
            return "\n".join(lines)

        max_count = max(counts.values()) if counts else 0

        lines.append(f"Total check-ins: {total}")
        lines.append("")

        for mood_key, label in self.mood_labels.items():
            count = counts.get(mood_key, 0)
            bar = self.build_bar(count, max_count, width=15) if max_count > 0 else ""
            lines.append(f"{label:<15} {count:>3} {bar}")

        return "\n".join(lines)

    # ---------------------------------------------------

    @app_commands.command(
        name="checkinstats",
        description="View stats of your moods over the last number of days."
    )
    @app_commands.describe(
        days="Number of days to look back (max 30)."
    )
    async def checkinstats(self, interaction: discord.Interaction, days: app_commands.Range[int, 1, 30]):

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
        counts, total = self.compute_stats(filtered)

        stats_text = self.format_stats_text(user, days, counts, total)

        # If short enough, use an embed
        if len(stats_text) <= 3500:
            lines = stats_text.split("\n")
            title = lines[0] if lines else "Daily Check-In Stats"
            desc = "\n".join(lines[2:]) if len(lines) > 2 else "No check-ins found in this time range."

            embed = discord.Embed(
                title=title,
                description=desc,
                color=0x4c9aff
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Fallback: send as text file
        file_buffer = io.BytesIO(stats_text.encode("utf-8"))
        discord_file = discord.File(file_buffer, filename="checkin_stats.txt")

        await interaction.response.send_message(
            content="Your check-in stats are a bit long, so here they are as a file:",
            file=discord_file,
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(CheckInStats(bot))
