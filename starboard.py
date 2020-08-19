from decouple import config
import discord
from discord.ext import commands

class Starboard(commands.Cog):
    def __init__(self, client):
        self.client = client


#client = commands.Bot(command_prefix = config('PREFIX'))


    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is ready.')


    @commands.Cog.listener()
    async def on_message(message):
        if message.content.startswith('hello'):
            await message.channel.send('Hi')
        if message.content.contains('shutdown'):
            await message.channel.send('Bye')
            await client.logout()
        if message.content.startswith('id#'):
            await message.channel.send(str(message.channel.id))
    #    if message.content.startswith('star'):
    #        await message.channel.send(str(emoji.id))


    @commands.Cog.listener()
    async def on_reaction_add(reaction, user):
        starboard = client.get_channel(int(config('STARBOARD_CHANNEL')))
        count = reaction.count
        if (reaction.emoji == '\U00002B50') & (count >= 1):
            #await starboard.send('stars: ' + str(count) + ' ' + reaction.emoji + message.content)
            embedVar = discord.Embed(title="link", url=reaction.message.jump_url, description = 'stars: ' + str(count) + ' ' + reaction.emoji + message.content)
            #embedVar.set_image(url = message.attatchment.url)
            await starboard.send(embed=embedVar)



    @commands.command()
    async def shutdown(self, ctx):
        await ctx.bot.logout()



def setup(client):
    client.add_cog(Starboard(client))


#client.run(config('DISCORD_TOKEN'))
