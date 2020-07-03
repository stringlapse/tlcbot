import discord
import random
from discord.ext import commands
from decouple import config

bot = commands.Bot(command_prefix = config('PREFIX'))

@bot.event
async def on_ready():
    print('Bot is ready.')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong')

@bot.command(aliases=['8ball', 'test'])
async def _8ball(ctx, *, question):
    responses = ['It is a fact.',
                'Winner winner, chicken dinner.',
                'Could it have been any different?',
                'Yes, definitely.',
                'Without a doubt.',
                'As I see it, yes.',
                'Outlook is favorable.',
                'Yes.',
                "It's only a matter of time.",
                'Signs point to yes.',
                'Ask again later.',
                'Have you been drinking enough water? Ask again.',
                'Better not tell you now.',
                'Concentrate and ask again.',
                'Nah fam.',
                'Not likely.',
                'Very doubtful.',
                'Yes, but only if you inlucde a friend.']
    await ctx.send(f'Q: {question}\nA: {random.choice(responses)}')

@bot.command()
async def joined(ctx, *, member: discord.Member):
    await ctx.send(f'{discord.member} joined on {member.joined_at}')

@bot.command()
@commands.has_role("devs")
# replace 'devs' with whatever the admin role for TLC is
async def clear(ctx, amount=1):
    await ctx.channel.purge(limit=amount+1)
    embed=discord.Embed(title=f'{amount} messages cleared!', color=0x228B22)
    await ctx.send(embed=embed)

bot.run(config('DISCORD_TOKEN'))