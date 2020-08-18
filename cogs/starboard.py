# An example of how a Cog should be properly instantiated

import discord
from discord.ext import commands

class Starboard(commands.Cog):
    def __init__(self, client):
        self.client = client

    
    @commands.Cog.listener()
    async def on_reaction_add(reaction, user):
        starboard = client.get_channel(734925342854086756)
        count = reaction.count
        if (reaction.emoji == '\U00002B50') & (count >= 1):
            await starboard.send('there were ' + str(count) + ' ' + reaction.emoji + '\n' + reaction.message.jump_url)
            embedVar = discord.Embed(title="Jump", url=reaction.message.jump_url)
            await starboard.send(embed=embedVar)


    
# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Starboard(client))
