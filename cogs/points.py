# cogs/points.py
import discord
from discord import app_commands
from discord.ext import commands
import database
from datetime import timedelta

class PointsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="givepoints", description="Give Contribution Points to a member.")
    @app_commands.describe(member="The member to give points to.", points="The amount of points to give.", reason="The reason for giving points.")
    @app_commands.checks.has_permissions(administrator=True)
    async def give_points(self, interaction: discord.Interaction, member: discord.Member, points: int, reason: str = None):
        """Admin command to give points to a single member."""
        if member.bot:
            await interaction.response.send_message("You cannot give points to a bot.", ephemeral=True)
            return

        database.add_points(member.id, interaction.guild.id, points, reason)
        
        embed = discord.Embed(
            title="Points Awarded!",
            color=discord.Color.green(),
            description=f"**{points}** Contribution Points awarded to {member.mention}."
        )
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="giverole", description="Give Contribution Points to all members in a role.")
    @app_commands.describe(role="The role to give points to.", points="The amount of points to give each member.", reason="The reason for giving points.")
    @app_commands.checks.has_permissions(administrator=True)
    async def give_role_points(self, interaction: discord.Interaction, role: discord.Role, points: int, reason: str = None):
        """Admin command to give points to all members of a role."""
        await interaction.response.defer(thinking=True) # Acknowledge the command, as this can take time

        members_awarded = 0
        for member in role.members:
            if not member.bot:
                database.add_points(member.id, interaction.guild.id, points, reason)
                members_awarded += 1
        
        embed = discord.Embed(
            title="Points Distributed to Role!",
            color=discord.Color.blue(),
            description=f"Awarded **{points}** Contribution Points to **{members_awarded}** members of the {role.mention} role."
        )
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="leaderboard", description="Check the Contribution Point leaderboards.")
    @app_commands.describe(timespan="The time period for the leaderboard.")
    @app_commands.choices(timespan=[
        app_commands.Choice(name="All Time", value="all"),
        app_commands.Choice(name="Past Month (30 days)", value="month"),
        app_commands.Choice(name="Past Week (7 days)", value="week"),
    ])
    async def leaderboard(self, interaction: discord.Interaction, timespan: str = "all"):
        """Displays the contribution leaderboard."""
        await interaction.response.defer(thinking=True)

        time_delta = None
        title = "All-Time Contribution Leaderboard"
        if timespan == "month":
            time_delta = timedelta(days=30)
            title = "Monthly Contribution Leaderboard (Last 30 Days)"
        elif timespan == "week":
            time_delta = timedelta(days=7)
            title = "Weekly Contribution Leaderboard (Last 7 Days)"
        
        leaderboard_data = database.get_leaderboard(interaction.guild.id, time_delta)

        embed = discord.Embed(title=f"🏆 {title}", color=discord.Color.gold())

        if not leaderboard_data:
            embed.description = "No contributions have been recorded for this period yet."
            await interaction.followup.send(embed=embed)
            return

        description = []
        for i, (user_id, total_points) in enumerate(leaderboard_data):
            rank_emote = {0: "🥇", 1: "🥈", 2: "🥉"}.get(i, f"**#{i+1}**")
            member = interaction.guild.get_member(user_id)
            member_name = member.display_name if member else f"User ID: {user_id}"
            description.append(f"{rank_emote} {member_name}: **{total_points}** points")
        
        embed.description = "\n".join(description)
        embed.set_footer(text="Points are the currency for upgrading your rank in Celestial Omens!")
        
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(PointsCog(bot))
