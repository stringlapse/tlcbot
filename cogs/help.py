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
    @commands.command(aliases=['commands', '?'])
    async def help(self, ctx, page="1"):
        # ["command", "simple description", "detailed description"]
        helpContent = [
        ["bingo", "Generates a random art prompt bingo card", ""], # Detailed description left blank as this is handled further down
        ["color", "Generates a random color", f"Can also be used to display a given color using `{config('PREFIX')}color #123456` (hex) or `{config('PREFIX')}color (12,34,56)` (rgb)."],
        ["colorphoto", "Picks out the most prominent colors from a picture", f"Upload a photo or include a link to get colors from it. You can also specify how many colors to get (3-6) and if you want complimentary colors. (ex. `{config('PREFIX')}colorphoto 5 complimentary https://via.placeholder.com/150`)"],
        ["cookies", "Shows how many cookies you have", f"Cookies are TLC's in-server point system, you can get them by:\n- Giving detailed and helpful critiques to others\n- Participating in monthly challenges, ongoing events, and `{config('PREFIX')}bingo`\n- Uplifting the community by having pleasant conversations with others\n- Inviting your friends over to TLC <:blobpinkspheart:635533584563961875>\n\n:cookie: Stock up so we can start a rewards program! [Hungry?](https://pastebin.com/dStYKpUb)"],
        ["leaderboard", "Show who has the most cookies", f"See `{config('PREFIX')}help cookies` for more info about cookies"],
        ["link", "Link your social media accounts", f"Use `{config('PREFIX')}link <platform> <account>` to link your social media accounts (ex. `{config('PREFIX')}link twitter tlc_discord`).\nCurrently supported platforms are Instagram, Twitter, YouTube, ArtStation, DeviantArt, TikTok, Twitch, and Personal Website (use `personal_website` for platform)"],
        ["prompt", "Generates a random art prompt", ""],
        ["scheme", f"Similar to {config('PREFIX')}color but generates a color scheme", f"By default generates a random color scheme but a color to base the scheme on may be specified. Format for specifying a color is `{config('PREFIX')}scheme #123456` (hex) or `{config('PREFIX')}scheme (12,34,56)` (rgb)."],
        ["sm", "Lists your or someone else's linked social media accounts", f"Use `{config('PREFIX')}sm @member` to see someone else's linked accounts or just `{config('PREFIX')}sm` to see yours. To set your social media accounts, see `{config('PREFIX')}help link`"],
        ["unlink", "Unlink your social media accounts", f"Use `{config('PREFIX')}unlink <platform>` to unlink a social media account (ex. `{config('PREFIX')}unlink twitter`).\nCurrently supported platforms are Instagram, Twitter, YouTube, ArtStation, DeviantArt, TikTok, Twitch, and Personal Website (use `personal_website` for platform)"]
        ]

        length = len(helpContent)
        if length%5 == 0:
            helpPages = (length//5)
        else:
            helpPages = (length//5)+1

        if page == "1" or page.isnumeric():
            try:
                page = int(page)
                pickedHelpContent = helpContent[(page-1)*5:(page-1)*5+5]
                helpEmbed = discord.Embed(title=f"Help (Page {page})", description=f"Use `{config('PREFIX')}help [1-{helpPages}]` for more", color=int(config("EMBED_COLOR"), 16))
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
            if page == "bingo":
                embed = discord.Embed(title=f"{config('PREFIX')}bingo",color=int(config("EMBED_COLOR"), 16))
                embed.add_field(name=":sparkles::sparkles::sparkles:BINGO:sparkles::sparkles::sparkles:",
                value=f"""-Submit an art based off prompts from a generated (`{config('PREFIX')}bingo`) card for 10 cookies!
                -Can use cards generated for other people.
                -You can “steal” (read: use) the same set of prompts from someone who has already submitted but your art receives 5 cookies instead. **No redraws, pls** <:blobcookie:622891874331394070>!  
                -Post your art here and caption it “Bingo!” along with the set of prompts you used (remember to cite/reply with someone else’s set of prompts if you did use theirs).
                
                Get aerting!""")
                embed.set_image(url="https://cdn.discordapp.com/attachments/746448871005094018/853711607675092992/bingo_help.jpg")
                return await ctx.send(embed=embed)
            if page == "cookie":
                embed = discord.Embed(title=f"{config('PREFIX')}cookie",color=int(config("EMBED_COLOR"), 16))
                embed.add_field(name=f"Perhaps you are looking for `{config('PREFIX')}help cookies`, and not Grandma's favorite recipe", value="""
                - Preheat oven to 375 degrees F (190 for them cultured folk). Line a baking pan with parchment paper and set aside.
                - In a separate bowl mix flour, baking soda, salt, baking powder. Set aside.
                - Cream together butter and sugars until combined.
                - Beat in eggs and vanilla until fluffy.
                - Mix in the dry ingredients until combined.
                - Add 12 oz package of chocolate chips and mix well.
                - Roll 2-3 TBS (depending on how large you like your cookies) of dough at a time into balls and place them evenly spaced on your prepared cookie sheets. (alternately, use a small cookie scoop to make your cookies).
                - Bake in preheated oven for approximately 8-10 minutes. Take them out when they are just BARELY starting to turn brown.
                - Let them sit on the baking pan for 2 minutes before removing to cooling rack.""", inline=False)
                return await ctx.send(embed=embed)
            found = False
            for entry in helpContent:
                if page == entry[0]:
                    found = True
                    if entry[2] == "":
                        await ctx.send("There's no extra help for that command")
                        break
                    extraHelpEmbed = discord.Embed(title=config('PREFIX')+entry[0], color=int(config("EMBED_COLOR"), 16))
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
        ["addbingoterm", "Adds a term for bingo (case taken literally)", "However you put the capitalization is how it will show up in bingo. Length is also important, long terms might overflow."],
        ["clear", "Deletes the number of messages specified", ""],
        ["eventcookie", "Creates a cookie event", f"Sends a message in announcements that users can react to to claim free cookies. Usage: `{config('PREFIX')}eventcookie amount end_date message`"],
        ["givecookie", "Give the mentioned member 5 cookies", f"See `{config('PREFIX')}help cookies` for info on cookies. Usage: `{config('PREFIX')}givecookie @member`"],
        ["givemultiplecookies", "Like givecookie but with a defined amount", f"The same as `{config('PREFIX')}givecookie` but with an amount at the end. Usage: `{config('PREFIX')}givemultiplecookies @member amount`"],
        ["load", "Loads a cog into the bot", ""],
        ["ping", "Responds pong", "Technically not a mod command but I figured I'd put it here since it can be used to test responsiveness"],
        ["reload", "Unloads and reloads a cog", "Useful for testing or I guess if the bot is acting up? idk just don't use it unless you know what you're doing"],
        ["removecookies", "Remove cookies from a user", "Works the same as givemultiplecookies but subtracts instead of adds"],
        ["restart", "⚠ Restarts the bot", "This should be safe for any mod to use but please ask someone on the bot team before using it"],
        ["shutdown", "⚠ Shuts the bot down", "Do not use this unless absolutely necessary. The bot will not restart on its own."],
        ["unload", "⚠ Uloads a cog from the bot", "This will disable all commands and functionality the cog provides."]]

        if len(modHelpContent)%5 == 0:
            modHelpPages = (len(modHelpContent)//5)
        else:
            modHelpPages = (len(modHelpContent)//5)+1

        if page == "1" or page.isnumeric():
            try:
                page = int(page)
                pickedModHelpContent = modHelpContent[(page-1)*5:(page-1)*5+5]
                modHelpEmbed = discord.Embed(title=f"Mod Help (Page {page})", description=f"Use `{config('PREFIX')}modhelp [1-{modHelpPages}]` for more", color=int(config("EMBED_COLOR"), 16))
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
                    extraModHelpEmbed = discord.Embed(title=config('PREFIX')+entry[0], color=int(config("EMBED_COLOR"), 16))
                    extraModHelpEmbed.add_field(name=entry[1], value=entry[2], inline=False)
                    await ctx.send(embed=extraModHelpEmbed)
                    break
            if not found:
                await ctx.send("That command doesn't exist")

# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Help(client))
