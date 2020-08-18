import discord
from discord.ext import commands


client = commands.Bot(command_prefix = '!')
#emoji = ':star:'


@client.event
async def on_ready():
    print('Bot is ready.')

"""
@client.event
async def on_member_join(member):
    print(f'{member} has joined a server.')

@client.event
async def on_member_remove(member):
    print(f'{member} has left a server.')
"""
@client.event
async def on_message(message):
    if message.content.startswith('hello'):
        await message.channel.send('Hi')
    if message.content.startswith('shutdown'):
        await message.channel.send('Bye')
        await client.logout()
    if message.content.startswith('id#'):
        await message.channel.send(str(message.channel.id))
#    if message.content.startswith('star'):
#        await message.channel.send(str(emoji.id))


@client.event
async def on_reaction_add(reaction, user):
    starboard = client.get_channel(734925342854086756)
    count = reaction.count
    if (reaction.emoji == '\U00002B50') & (count >= 1):
        await starboard.send('there were ' + str(count) + ' ' + reaction.emoji + '\n' + reaction.message.jump_url)
        embedVar = discord.Embed(title="Jump", url=reaction.message.jump_url)
        await starboard.send(embed=embedVar)


@client.command()
async def ping(ctx):
    await ctx.send(f'pong {round(client.latency * 1000)}ms')

@client.command()
async def shutdown(ctx):
    await ctx.bot.logout()

"""
@client.command()
async def hello(ctx):
    await ctx.send(f'hello {ctx.author}!')

"""

client.run('NzMwNTc5OTQwMjM5NzM2OTAz.XwZjyg.tCBQaR2H9ncvlo643et0wPicmSY')
