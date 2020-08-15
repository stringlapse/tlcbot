# An example of how a Cog should be properly instantiated

import discord
from discord.ext import commands

class Commission(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Events: make sure to pass in 'self' 
    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online.")
    
    # Commands
    @commands.command()
    async def setCommission(self, ctx):
        await ctx.send("Pong!")

# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Commission(client))
