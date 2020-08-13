import discord
import random
import re
from discord.ext import commands
from decouple import config

class Tabletop(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def roll(self, ctx, sides, amount):
      try:
        m = re.search('\d', sides)
        sidesDice = int(m.group(0))
        rolls_list = []
        for number in range(int(amount)):
          # 1 is the minimum number the dice can have
          rolls_list.append(random.randint(1, sides))
        rolls = ", ".join(str(number) for number in rolls_list)
        await ctx.send("Your dice rolls were: " + rolls)
      except Exception as e:
        # You should catch different exceptions for each problem and then handle them
        # Exception is too broad
        print(e)
        await ctx.send(f"Incorrect format for sides of dice (try something like ``{config('PREFIX')}roll d6 1``).")

# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Tabletop(client))
