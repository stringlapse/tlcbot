import discord
import random
import os
from discord.ext import commands
from decouple import config

bot = commands.Bot(command_prefix = config('PREFIX'))

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

def embedsText(title, description):
    if title == '':
        return discord.Embed(description=description, color=0x228B22)
    elif description == '':
        return discord.Embed(title=title, color=0x228B22)
    else:
        return discord.Embed(description=description, title=title, color=0x228B22)

# loads cogs into bot
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(config('DISCORD_TOKEN'))