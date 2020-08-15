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

        helpPages = (len(helpContent)//5)+1

        try:
            pickedHelpContent = helpContent[(page-1)*5:(page-1)*5+5]
            helpEmbed = discord.Embed(title=f"Help (Page {page})", description=f"Use `{config('PREFIX')}help [1-{helpPages}]` for more", color=0x00ff00) # Update with number of pages later
            for i in range(0, 5):
                try:
                    helpEmbed.add_field(name=pickedHelpContent[i][0], value=pickedHelpContent[i][1], inline=False)
                    if i == 4:
                        await ctx.send(embed=helpEmbed)
                except IndexError:
                    if i == 0:
                        await ctx.send(f"There are only {helpPages} pages of help. Use `{config('PREFIX')}help [1-{helpPages}]` for help.") # Update with number of pages later
                        break
                    else:
                        await ctx.send(embed=helpEmbed)
                        break
        except IndexError:
            await ctx.send(f"There are only {helpPages} pages of help. Use `{config('PREFIX')}help [1-{helpPages}]` for help.") # Update with number of pages later

    @commands.command()
    @commands.has_role(admin_role)
    async def modhelp(self, ctx, page=1):
        modHelpContent = [
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
        ["LL", "ll"],
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
        ["LL", "ll"],
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

        modHelpPages = (len(modHelpContent)//5)+1

        try:
            pickedModHelpContent = modHelpContent[(page-1)*5:(page-1)*5+5]
            modHelpEmbed = discord.Embed(title=f"Mod Help (Page {page})", description=f"Use `{config('PREFIX')}modhelp [1-{modHelpPages}]` for more", color=0x00ff00) # Update with number of pages later
            for i in range(0, 5):
                try:
                    modHelpEmbed.add_field(name=pickedModHelpContent[i][0], value=pickedModHelpContent[i][1], inline=False)
                    if i == 4:
                        await ctx.send(embed=modHelpEmbed)
                except IndexError:
                    if i == 0:
                        await ctx.send(f"There are only {modHelpPages} pages of mod help. Use `{config('PREFIX')}modhelp [1-{modHelpPages}]` for mod help.") # Update with number of pages later
                        break
                    else:
                        await ctx.send(embed=modHelpEmbed)
                        break
        except IndexError:
            await ctx.send(f"There are only {modHelpPages} pages of mod help. Use `{config('PREFIX')}modhelp [1-{modHelpPages}]` for mod help.") # Update with number of pages later

# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Help(client))
