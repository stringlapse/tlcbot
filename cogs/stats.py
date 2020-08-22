# An example of how a Cog should be properly instantiated

import discord
import sqlite3
import asyncio
import traceback
from discord.ext import tasks, commands
from datetime import date
from decouple import config

class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.checkDay.start()
    
    # Creates the day and member stat counter channels if not in the server. Updates them if they are.
    @commands.Cog.listener()
    async def on_ready(self):
        await self.updateMemberCount()
        await self.updateDayCount()


    # Recalculates the member count if someone new joins
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.updateMemberCount()
    
    # Recalculates the member count if someone leaves
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.updateMemberCount()
    
    # Cron job (well it's a discord task) to update the day stat every hour. I avoided doing every 24 hours
    # Because if you start the bot at two in the afternoon the day counter wont really switch until that time
    # All this code does is continually check if the day has changed and if so it updates the date accordingly.
    @tasks.loop(hours=1.0)
    async def checkDay(self):
        await self.updateDayCount()
        
    
    # Code necessary for the task 
    @checkDay.before_loop
    async def checkDay_before(self):
        await self.client.wait_until_ready()
    
    # Function to recalculate the number of members and "update" the channels
    # as oppose to adding and subtracting of someone joins or leaves, which may
    # lead to innacuracies 
    async def updateMemberCount(self):
        guild = self.client.get_guild(int(config('GUILD_ID')))
        categoryName = "Server Stats"
        category = discord.utils.get(guild.categories, name=categoryName)

        if category is None:
            category = await guild.create_category(categoryName)

        memberCount = guild.member_count
        memberText = f'Member Count: {memberCount}'

        memberChannel = False
        for channel in guild.voice_channels:
            if "Member Count" in channel.name:
                memberChannel = True
                await channel.edit(name = memberText)  
        if not (memberChannel):
            channel = await guild.create_voice_channel(name=memberText,category=category)
            await channel.set_permissions(guild.default_role, connect=False)
    
    async def updateDayCount(self):
        guild = self.client.get_guild(int(config('GUILD_ID')))
        categoryName = "Server Stats"
        category = discord.utils.get(guild.categories, name=categoryName)

        if category is None:
            category = await guild.create_category(categoryName)

        delta = countsDays()
        daysText = f'Days Open: {delta}'

        dayChannel = False
        for channel in guild.voice_channels:
            if "Days Open" in channel.name:
                dayChannel = True
                await channel.edit(name = daysText)  
        if not (dayChannel):
            channel = await guild.create_voice_channel(name=daysText,category=category)
            await channel.set_permissions(guild.default_role, connect=False)

# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Stats(client))

# Returns how many days it has been since the server's opening
def countsDays():
    return (date.today() - date(2019,8,23)).days





