import discord
import random
import os
from discord.ext import commands
from decouple import config

bot = commands.Bot(command_prefix = config('PREFIX'))
bot.remove_command('help') # Remove default help command so we can implement our own

admin_role = "Mod"

@bot.command()
@commands.has_role(admin_role)
async def load(ctx, extension):
    await ctx.send(f"Loading {extension}...")
    print(f"{str(ctx.message.author)} (id {str(ctx.message.author.id)}) loaded {extension}")
    bot.load_extension(f'cogs.{extension}')

@bot.command()
@commands.has_role(admin_role)
async def unload(ctx, extension):
    await ctx.send(f"Unloading {extension}...")
    print(f"{str(ctx.message.author)} (id {str(ctx.message.author.id)}) unloaded {extension}")
    bot.unload_extension(f'cogs.{extension}')

@bot.command()
@commands.has_role(admin_role)
async def reload(ctx, extension):
    await ctx.send(f"Reloading {extension}...")
    print(f"{str(ctx.message.author)} (id {str(ctx.message.author.id)}) reloaded {extension}")
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')

@bot.command()
@commands.has_role(admin_role)
async def shutdown(ctx):
    await ctx.send("Shutting down bot...")
    print(f"{str(ctx.message.author)} (id {str(ctx.message.author.id)}) requested a shutdown")
    await bot.close()

@bot.command()
@commands.has_role(admin_role)
async def restart(ctx):
    await ctx.send("Restarting bot...")
    print(f"{str(ctx.message.author)} (id {str(ctx.message.author.id)}) requested a restart")
    await bot.close()
    os.execl("/bin/bash", "/bin/bash", "./run.sh")

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