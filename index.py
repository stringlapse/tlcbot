import discord
import random
import os
from discord.ext import commands
from decouple import config

bot = commands.Bot(command_prefix = config('PREFIX'))

admin_role = "devs"

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

@bot.command()
@commands.has_role(admin_role)
async def shutdown(ctx):
    await ctx.send("Shutting down bot...")
    print(f"{str(ctx.message.author)} (id {str(ctx.message.author.id)}) requested a shutdown")
    await bot.close()

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