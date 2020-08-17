# An example of how a Cog should be properly instantiated

import discord
import sqlite3
import aiocron
import asyncio
from discord.ext import commands
from datetime import date
from decouple import config

class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    # Creates the day and member stat counter channels if not in the server. Updates them if they are.
    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.client.get_guild(int(config('GUILD_ID')))
        memberCount = len([m for m in guild.members if not m.bot])

        delta = countsDays()
        daysText = f'Days Open: {delta}'

        categoryName = "Server Stats"
        memberText = f'Member Count: {memberCount}'
       

        category = discord.utils.get(guild.categories, name=categoryName)
        if category is None:
            category = await guild.create_category(categoryName)
        
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute('SELECT channel_id FROM channel WHERE function = ?', ('memberCount',))
        result = c.fetchone()
        if result is None:
            channel = await guild.create_voice_channel(name=memberText,category=category)
            await channel.set_permissions(guild.default_role, connect=False)
            c.execute("INSERT INTO channel(channel_id,function) VALUES(?,?)", (channel.id,'memberCount'))   
        else:
            await self.updateCount(result, guild)
        
        c.execute('SELECT channel_id FROM channel WHERE function = ?', ('dayCount',))
        result = c.fetchone()
        if result is None:
            channel = await guild.create_voice_channel(name=daysText,category=category)
            await channel.set_permissions(guild.default_role, connect=False)
            c.execute("INSERT INTO channel(channel_id,function) VALUES(?,?)", (channel.id,'dayCount')) 
        else:
            channel = guild.get_channel(int(result[0]))
            await channel.edit(name=daysText)

        conn.commit()
        conn.close()   
            

    # Deletes the channel from the database if it gets deleted on the server (avoids error of
    # the channel existing on the database and the bot searching for a channel in the database
    # that no longer exists)
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        print('channel got deleted')
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute('SELECT * FROM channel WHERE channel_id = ?', (channel.id,))
        result = c.fetchone()
        if result is not None:
            c.execute("DELETE FROM channel WHERE channel_id = ?", (str(channel.id),))
            conn.commit()
            conn.close()

    # Recalculates the member count if someone new joins
    @commands.Cog.listener()
    async def on_member_join(self, member):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute('SELECT * FROM channel WHERE function = ?', ('memberCount',))
        result = c.fetchone()

        if result is not None:
            await self.updateCount(result, member.guild)
    
    # Recalculates the member count if someone leaves
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute('SELECT * FROM channel WHERE function = ?', ('memberCount',))
        result = c.fetchone()

        if result is not None:
            await self.updateCount(result, member.guild)
    
    # Cron job to update the day stat every midnight
    @aiocron.crontab('0 0 * * *')
    async def updateDay(self):
        print("cron cron")
        delta = countsDays()
        daysText = f'Days Open: {delta}'
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute('SELECT channel_id FROM channel WHERE function = ?', ('dayCount',))
        result = c.fetchone()
        if result is not None:
            channel = guild.get_channel(int(result[0]))
        await channel.edit(name=daysText)
    
    # Function to recalculate the number of members and "update" the channels
    # as oppose to adding and subtracting of someone joins or leaves, which may
    # lead to innacuracies 
    async def updateCount(self, result, guild):
        memberCount = len([m for m in guild.members if not m.bot])
        categoryName = "Server Stats"
        memberText = f'Member Count: {memberCount}'
        if result is not None:
            channel = guild.get_channel(int(result[0]))
            await channel.edit(name=memberText)
        
# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Stats(client))

# Returns how many days it has been since the server's opening
def countsDays():
    return (date.today() - date(2019,8,22)).days


