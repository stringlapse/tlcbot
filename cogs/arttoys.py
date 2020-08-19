from nltk import CFG
import random
from nltk.parse.generate import generate
import discord
from discord.ext import commands
from decouple import config
from index import embedsText

#for i in range(1,100):
#    prompt()

botID = int(config('BOT_ID'))
bot = commands.Bot(command_prefix=config('PREFIX'))

class ArtToys(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.grammar = CFG.fromstring(open("default_grammar.cfg").read())
        self.all_prompts = list(generate(self.grammar))
        print(str(len(self.all_prompts)) + " prompts loaded")

    async def gen(self):
        prompt = ' '.join(random.choice(self.all_prompts))
        #print(prompt)
        return (prompt)

    @bot.command()
    async def prompt(self,ctx):
        user = self.client.get_user(ctx.message.author.id)
        embed = embedsText(await self.gen(),'')
        embed.set_author (name="Art prompt for " + str(user),icon_url=user.avatar_url)
        embed.set_footer(text="react with 🔁 to reroll.")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('🔁')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,ctx):
        #print(ctx)
        if(ctx.user_id != botID and ctx.emoji.name == "🔁" and ctx.event_type == "REACTION_ADD"):
            #print("reaction not made by bot")
            channel = self.client.get_channel(ctx.channel_id)
            msg = await channel.fetch_message(ctx.message_id)
            user = self.client.get_user(ctx.user_id)
            if(msg.author.id == botID and msg.embeds[0] and msg.embeds[0].author.name == "Art prompt for " + str(user)):
                embed = embedsText(await self.gen(),'')
                embed.set_author (name="Art prompt for " + str(user),icon_url=user.avatar_url)
                embed.set_footer(text="react with 🔁 to reroll.")
                await msg.edit(embed=embed)
                await msg.remove_reaction("🔁",user)
                #print("reaction on message made by bot")
                #print(msg)
            pass

# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(ArtToys(client))

