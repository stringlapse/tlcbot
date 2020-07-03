# An example of how a Cog should be properly instantiated

import discord
from discord.ext import commands

class Example(commands.Cog):
    def __init__(self, client):
        self.client = client

<<<<<<< HEAD
    # Events: make sure to pass in 'self' 
=======
    # Events
>>>>>>> a7e99771c7deed4b0d6199aad3b0fe6b83d4e2ae
    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online.")
    
    # Commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")
    
<<<<<<< HEAD
    @commands.command(aliases=['8ball', 'test'])
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
=======
    # @commands.command(aliases=['8ball', 'test'])
    # async def _8ball(ctx, *, question):
    #     responses = ['It is a fact.',
    #                 'Winner winner, chicken dinner.',
    #                 'Could it have been any different?',
    #                 'Yes, definitely.',
    #                 'Without a doubt.',
    #                 'As I see it, yes.',
    #                 'Outlook is favorable.',
    #                 'Yes.',
    #                 "It's only a matter of time.",
    #                 'Signs point to yes.',
    #                 'Ask again later.',
    #                 'Have you been drinking enough water? Ask again.',
    #                 'Better not tell you now.',
    #                 'Concentrate and ask again.',
    #                 'Nah fam.',
    #                 'Not likely.',
    #                 'Very doubtful.',
    #                 'Yes, but only if you inlucde a friend.']
    #     await ctx.send(f'Q: {question}\nA: {random.choice(responses)}')
>>>>>>> a7e99771c7deed4b0d6199aad3b0fe6b83d4e2ae

    @commands.command()
    async def joined(ctx, *, member: discord.Member):
        await ctx.send('{discord.member} joined on {0.joined_at}'.format(member))

<<<<<<< HEAD
# Required for the cog to be read by the bot
=======
>>>>>>> a7e99771c7deed4b0d6199aad3b0fe6b83d4e2ae
def setup(client):
    client.add_cog(Example(client))
