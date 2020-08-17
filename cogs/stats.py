# An example of how a Cog should be properly instantiated

import discord
import sqlite3
from discord.ext import commands
from decouple import config

class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.client.get_guild(int(config('GUILD_ID')))
        memberCount = len([m for m in guild.members if not m.bot])
        categoryName = "Server Stats"
        channelName = f'Member Count: {memberCount}'
        
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute('SELECT channel_id FROM channel WHERE function = ?', ('memberCount',))
        result = c.fetchone()
        if result is None:
            category = discord.utils.get(guild.categories, name=categoryName)
            if category is None:
                category = await guild.create_category(categoryName)
            channel = await guild.create_voice_channel(name=channelName,category=category)
            await channel.set_permissions(guild.default_role, connect=False)
            c.execute("INSERT INTO channel(channel_id,function) VALUES(?,?)", (channel.id,'memberCount')) 
            conn.commit()
            conn.close()   
        else:
            await self.updateCount(result, guild)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        print('channel got deleted')
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute('SELECT * FROM channel WHERE channel_id = ?', (channel.id,))
        result = c.fetchone()
        if result is not None:
            c.execute("DELETE FROM channel WHERE channel_id =?", (str(channel.id),))
            conn.commit()
            conn.close()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute('SELECT * FROM channel WHERE function = ?', ('memberCount',))
        result = c.fetchone()

        if result is not None:
            await self.updateCount(result, member.guild)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute('SELECT * FROM channel WHERE function = ?', ('memberCount',))
        result = c.fetchone()

        if result is not None:
            await self.updateCount(result, member.guild)
    
    async def updateCount(self, result, guild):
        memberCount = len([m for m in guild.members if not m.bot])
        channelName = f'Member Count: {memberCount}'
        channel = guild.get_channel(int(result[0]))
        await channel.edit(name=channelName)

        
# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Stats(client))
