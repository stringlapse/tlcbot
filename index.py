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
async def clear(ctx, amount=1):
    await ctx.channel.purge(limit = amount)

@bot.command()
async def joined(ctx, *, member: discord.Member):
    await ctx.send('{discord.member} joined on {0.joined_at}'.format(member))

@bot.command()
@commands.has_role("devs")
# replace 'devs' with whatever the admin role for TLC is
async def mute(ctx, member: discord.Member):
    role = discord.utils.get(member.guild.roles, name = 'muted')
    await member.add_roles(role)
    embed=discord.Embed(title="User Muted!", description="**{0}** was muted by **{1}**!".format(member, ctx.message.author), color=0x228B22)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_role("devs")
# replace 'devs' with whatever the admin role for TLC is
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(member.guild.roles, name = 'muted')
    if role in member.roles:
        await member.remove_roles(role)
        embed=discord.Embed(title="User Unmuted!", description="**{0}** was unmuted by **{1}**!".format(member, ctx.message.author), color=0x228B22)
        await ctx.send(embed=embed)
    else:
        await ctx.send("**{0}** is not currently muted".format(member))




bot.run(config('DISCORD_TOKEN'))