# An example of how a Cog should be properly instantiated

import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Commands
    @commands.command()
    async def help(self, ctx):
        await ctx.send("generic help text placeholder")

# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Help(client))
