# An example of how a Cog should be properly instantiated

import discord
from discord.ext import commands
from index import admin_role
from decouple import config

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Commands
    @commands.command()
    async def help(self, ctx, page=1):
        helpContent = [
        ["AA", "aa"],
        ["BB", "bb"],
        ["CC", "cc"],
        ["DD", "dd"],
        ["EE", "ee"],
        ["FF", "ff"],
        ["GG", "gg"],
        ["HH", "hh"],
        ["II", "ii"],
        ["JJ", "jj"],
        ["KK", "kk"],
        ["LL", "ll"]]

        try:
            pickedHelpContent = helpContent[(page-1)*5:(page-1)*5+5]
            helpEmbed = discord.Embed(title=f"Help (Page {page})", description=f"Use `{config('PREFIX')}help [1-{(len(helpContent)//5)+1}]` for more", color=0x00ff00) # Update with number of pages later
            for i in range(0, 5):
                try:
                    helpEmbed.add_field(name=pickedHelpContent[i][0], value=pickedHelpContent[i][1], inline=False)
                    if i == 4:
                        await ctx.send(embed=helpEmbed)
                except IndexError:
                    if i == 0:
                        await ctx.send(f"There are only {(len(helpContent)//5)+1} pages of help. Use `{config('PREFIX')}help [1-{(len(helpContent)//5)+1}]` for help.") # Update with number of pages later
                        break
                    else:
                        await ctx.send(embed=helpEmbed)
                        break
        except IndexError:
            await ctx.send(f"There are only {(len(helpContent)//5)+1} pages of help. Use `{config('PREFIX')}help [1-{(len(helpContent)//5)+1}]` for help.") # Update with number of pages later

    @commands.command()
    @commands.has_role(admin_role)
    async def modhelp(self,ctx):
        await ctx.send("generic mod help text placeholder")

# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Help(client))
