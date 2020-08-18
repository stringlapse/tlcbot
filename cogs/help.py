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
    async def help(self, ctx, page="1"):
        helpContent = [
        ["aa", "AA", "aa detailed description"],
        ["bb", "BB", "bb detailed description"],
        ["cc", "CC", "cc detailed description"],
        ["dd", "DD", "dd detailed description"],
        ["ee", "EE", "ee detailed description"],
        ["ff", "FF", "ff detailed description"],
        ["gg", "GG", "gg detailed description"],
        ["hh", "HH", "hh detailed description"],
        ["ii", "II", "ii detailed description"],
        ["jj", "JJ", "jj detailed description"],
        ["kk", "KK", "kk detailed description"],
        ["ll", "LL", "ll detailed description"],
        ["mm", "MM", ""],
        ["cookies", "Shows how many cookies the user has", "Cookies are a valuable resource for TLC, you can get them by:\n - bumping the server with disboard or discord.me\n - giving detailed and helpful critiques to others\n - uplifting the community by having pleasant conversations with others\n\n🍪 Stock up on them so we can start a rewards program!"]]

        helpPages = (len(helpContent)//5)+1

        if page == "1" or page.isnumeric():
            try:
                page = int(page)
                pickedHelpContent = helpContent[(page-1)*5:(page-1)*5+5]
                helpEmbed = discord.Embed(title=f"Help (Page {page})", description=f"Use `{config('PREFIX')}help [1-{helpPages}]` for more", color=0x00ff00)
                for i in range(0, 5):
                    try:
                        helpEmbed.add_field(name=config('PREFIX')+pickedHelpContent[i][0], value=pickedHelpContent[i][1], inline=False)
                        if i == 4:
                            await ctx.send(embed=helpEmbed)
                    except IndexError:
                        if i == 0:
                            await ctx.send(f"There are only {helpPages} pages of help. Use `{config('PREFIX')}help [1-{helpPages}]` for help.")
                            break
                        else:
                            await ctx.send(embed=helpEmbed)
                            break
            except IndexError:
                await ctx.send(f"There are only {helpPages} pages of help. Use `{config('PREFIX')}help [1-{helpPages}]` for help.")
        else:
            page = page.lower()
            found = False
            for entry in helpContent:
                if page == entry[0]:
                    found = True
                    if entry[2] == "":
                        await ctx.send("There's no extra help for that command")
                        break
                    extraHelpEmbed = discord.Embed(title=config('PREFIX')+entry[0], color=0x00ff00)
                    extraHelpEmbed.add_field(name=entry[1], value=entry[2], inline=False)
                    await ctx.send(embed=extraHelpEmbed)
                    break
            if not found:
                await ctx.send("That command doesn't exist")

    @commands.command()
    @commands.has_role(admin_role)
    async def modhelp(self, ctx, page="1"):
        modHelpContent = [
        ["aa", "AA","generic filler content"],
        ["bb", "BB","generic filler content"],
        ["cc", "CC","generic filler content"],
        ["dd", "DD","generic filler content"],
        ["ee", "EE","generic filler content"],
        ["ff", "FF","generic filler content"],
        ["gg", "GG","generic filler content"],
        ["hh", "HH","generic filler content"],
        ["ii", "II","generic filler content"],
        ["jj", "JJ","generic filler content"],
        ["kk", "KK","generic filler content"],
        ["ll", "LL","generic filler content"],
        ["aa", "AA","generic filler content"],
        ["bb", "BB","generic filler content"],
        ["cc", "CC","generic filler content"],
        ["dd", "DD","generic filler content"],
        ["ee", "EE","generic filler content"],
        ["ff", "FF","generic filler content"],
        ["gg", "GG","generic filler content"],
        ["hh", "HH","generic filler content"],
        ["ii", "II","generic filler content"],
        ["jj", "JJ","generic filler content"],
        ["kk", "KK","generic filler content"],
        ["ll", "LL","generic filler content"],
        ["aa", "AA","generic filler content"],
        ["bb", "BB","generic filler content"],
        ["cc", "CC","generic filler content"],
        ["dd", "DD","generic filler content"],
        ["ee", "EE","generic filler content"],
        ["ff", "FF","generic filler content"],
        ["gg", "GG","generic filler content"],
        ["hh", "HH","generic filler content"],
        ["ii", "II","generic filler content"],
        ["jj", "JJ","generic filler content"],
        ["kk", "KK","generic filler content"],
        ["ll", "LL",""]]

        modHelpPages = (len(modHelpContent)//5)+1

        if page == "1" or page.isnumeric():
            try:
                page = int(page)
                pickedModHelpContent = modHelpContent[(page-1)*5:(page-1)*5+5]
                modHelpEmbed = discord.Embed(title=f"Mod Help (Page {page})", description=f"Use `{config('PREFIX')}modhelp [1-{modHelpPages}]` for more", color=0x00ff00)
                for i in range(0, 5):
                    try:
                        modHelpEmbed.add_field(name=config('PREFIX')+pickedModHelpContent[i][0], value=pickedModHelpContent[i][1], inline=False)
                        if i == 4:
                            await ctx.send(embed=modHelpEmbed)
                    except IndexError:
                        if i == 0:
                            await ctx.send(f"There are only {modHelpPages} pages of mod help. Use `{config('PREFIX')}modhelp [1-{modHelpPages}]` for mod help.")
                            break
                        else:
                            await ctx.send(embed=modHelpEmbed)
                            break
            except IndexError:
                await ctx.send(f"There are only {modHelpPages} pages of mod help. Use `{config('PREFIX')}modhelp [1-{modHelpPages}]` for mod help.")
        else:
            page = page.lower()
            found = False
            for entry in modHelpContent:
                if page == entry[0]:
                    found = True
                    if entry[2] == "":
                        await ctx.send("There's no extra help for that command")
                        break
                    extraModHelpEmbed = discord.Embed(title=config('PREFIX')+entry[0], color=0x00ff00)
                    extraModHelpEmbed.add_field(name=entry[1], value=entry[2], inline=False)
                    await ctx.send(embed=extraModHelpEmbed)
                    break
            if not found:
                await ctx.send("That command doesn't exist")

# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Help(client))
