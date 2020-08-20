# ============================================================
# There are two lists of help data, try to avoid putting your
# command in the wrong one. Standard help is first, mod help
# is second. The format is
# ["command", "simple description", "detailed description"]
# If you aren't writing a detailed description leave an empty
# string. These lists are manually alphabetized because it's
# probably faster not to reorder the list every time someone
# uses the help command. Put your command where it belongs in
# the list alphabetically.

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
        # ["command", "simple description", "detailed description"]
        helpContent = [
        ["bingo", "Generates a random art prompt bingo card", "Draw something that uses the prompts in all 5 squares in any line. Diagonal lines count, TLC is a free space. Don't forget to shout bingo and share your drawing when you're done!"],
        ["cookies", "Shows how many cookies the user has", "Cookies are a valuable resource for TLC, you can get them by:\n - bumping the server with disboard or discord.me\n - giving detailed and helpful critiques to others\n - uplifting the community by having pleasant conversations with others\n\n🍪 Stock up on them so we can start a rewards program!"],
        ["prompt", "Generates a random art prompt", ""]]

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
        # ["command", "simple description", "detailed description"]
        modHelpContent = [
        ["restart", "⚠ Restarts the bot","This should be safe for any mod to use but please ask someone on the bot team before using it"],
        ["shutdown", "⚠ Shuts the bot down","Do not use this unless absolutely necessary. The bot will not restart on its own."]]

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
