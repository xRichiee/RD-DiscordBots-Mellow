import discord
from discord import app_commands
from discord.ext import commands
import json
import random
from pathlib import Path

MAP_PATH = Path("Modules/Maps/Coping.json")


class CopingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Load JSON map
        try:
            with MAP_PATH.open("r", encoding="utf-8") as f:
                self.coping_map = json.load(f)
        except Exception as e:
            print(f"[CopingCog] Failed to load {MAP_PATH}: {e}")
            self.coping_map = {}

    # --------------------------------------------------------
    # Autocomplete for /cope
    # --------------------------------------------------------
    async def topic_autocomplete(self, interaction: discord.Interaction, current: str):
        current = current.lower()
        suggestions = []

        for topic in self.coping_map.keys():
            if current in topic:
                suggestions.append(app_commands.Choice(name=topic, value=topic))

        return suggestions[:25]  # Discord limit

    # --------------------------------------------------------
    # /cope
    # --------------------------------------------------------
    @app_commands.command(
        name="cope",
        description="Get a simple coping exercise based on what you're feeling."
    )
    @app_commands.describe(topic="Choose a coping topic")
    @app_commands.autocomplete(topic=topic_autocomplete)
    async def cope(self, interaction: discord.Interaction, topic: str):

        topic = topic.lower().strip()

        if topic not in self.coping_map:
            await interaction.response.send_message(
                "I don’t have a coping exercise for that yet — more are coming soon 💙",
                ephemeral=True
            )
            return

        # Get list of responses for the topic
        responses = self.coping_map[topic].get("responses", [])

        if not responses:
            await interaction.response.send_message(
                "Something went wrong — no responses available for this topic 💛",
                ephemeral=True
            )
            return

        # Pick a random response
        data = random.choice(responses)

        # Build embed
        embed = discord.Embed(
            title=data.get("title", "Coping Exercise"),
            description=data.get("description", ""),
            color=int(data.get("color", "85C1E9"), 16)
        )

        embed.add_field(
            name="More Support",
            value=f"[{data.get('link_text', 'Learn more')}]({data.get('link_url', '')})",
            inline=False
        )

        # Send privately
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(CopingCog(bot))
