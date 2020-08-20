from nltk import CFG
import random
#from nltk.parse.generate import generate
import discord
from discord.ext import commands
from decouple import config
from index import embedsText
from PIL import Image, ImageDraw, ImageFont
import random
from random import randrange
from io import BytesIO

#for i in range(1,100):
#    prompt()

botID = int(config('BOT_ID'))
bot = commands.Bot(command_prefix=config('PREFIX'))
bingoChannel = int(config('MOD_BINGO_CHANNEL'))

prompt_charprops = open("arttoys_prompts/charprops.cfg").read().split("\n")
prompt_chars = open("arttoys_prompts/chars.cfg").read().split("\n")
prompt_colors = open("arttoys_prompts/colors.cfg").read().split("\n")
prompt_scenery = open("arttoys_prompts/scenery.cfg").read().split("\n")
prompt_sceneryprops = open("arttoys_prompts/sceneryprops.cfg").read().split("\n")

class ArtToys(commands.Cog):
    def __init__(self, client):
        self.client = client
        #self.grammar = CFG.fromstring(open("default_grammar.cfg").read())
        self.bingo = open("bingo.cfg").read().split("\n")
        #self.all_prompts = list(generate(self.grammar))
        print(str(len(self.bingo)) + " bingo elements loaded")
        #print(str(len(self.all_prompts)) + " prompts loaded")

    async def gen(self):
        #prompt = ' '.join(random.choice(self.all_prompts))
        #print(prompt)
        if random.random() < 0.05: # 1/20 chance to omit charprop
            prompt = random.choice(prompt_chars)+' '+random.choice(prompt_scenery).format(sceneryprop=random.choice(prompt_sceneryprops))    
        else:
            prompt = random.choice(prompt_chars)+' '+random.choice(prompt_charprops).format(color=random.choice(prompt_colors))+' '+random.choice(prompt_scenery).format(sceneryprop=random.choice(prompt_sceneryprops))
        return (prompt)

    @bot.command()
    async def prompt(self,ctx):
        user = self.client.get_user(ctx.message.author.id)
        embed = embedsText(await self.gen(),'')
        embed.set_author (name="Art prompt for " + user.name,icon_url=user.avatar_url)
        embed.set_footer(text="🔁 to reroll.")
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
            if(msg.author.id == botID and msg.embeds[0] and msg.embeds[0].author.name == "Art prompt for " + str(user).split("#")[0]):
                embed = embedsText(await self.gen(),'')
                embed.set_author (name="Art prompt for " + user.name,icon_url=user.avatar_url)
                embed.set_footer(text="🔁 to reroll.")
                await msg.edit(embed=embed)
                await msg.remove_reaction("🔁",user)
                #print("reaction on message made by bot")
                #print(msg)
            pass

    @bot.command()
    async def bingo(self,ctx):
        img = Image.new('RGB', (1000, 1000), color = (255, 255, 255))
        d = ImageDraw.Draw(img)
        fnt = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 26)
        tlclogo = Image.open("tlc_logo.png")
        random.shuffle(self.bingo)
        _, h = d.textsize("qh")
        elements = self.bingo[:25]
        for i in range(0,5):
            d.line((0,i*200,1000,i*200),fill=(0,0,0),width=5)
            d.line((i*200,0,i*200,1000),fill=(0,0,0),width=5)
            for j in range(0,5):
                if i != 2 or j != 2:
                    text = elements[i*5+j]
                    w, _ = d.textsize(text,font=fnt)
                    d.text((i*200 + (200-w)/2,j*200+(200-h)/2), text, fill=(randrange(0,150),randrange(0,150),randrange(0,150)),font=fnt)
                # else:
                #     text = "TLC BINGO"
                #     w, h = d.textsize(text,font=fnt)
                #     print(i)
                #     print(i*200 + (200-w)/2)
                #     print(j)
                #     print(j*200 + (200-h)/2)
                #     d.text((i*200+(200-w)/2,j*200+(200-h)/2),"TLC BINGO",fill=(255,0,0),font=fnt)
        #print(type(img))
        img.paste(tlclogo,(402,402),tlclogo)
        img.save("images/bingo.png")
        buffer = BytesIO()
        img.save(buffer,"png")
        buffer.seek(0)
        file = discord.File(filename="tlcbingo.png", fp=buffer)
        bot_msg = await self.client.get_channel(bingoChannel).send(file=file)
        embed = embedsText("Art Bingo!","Draw an image that would score a bingo on the following sheet. Don't forget to shout bingo and share your finished drawing!")
        user = self.client.get_user(ctx.message.author.id)
        embed.set_author (name="TLC Bingo card for " + str(user).split("#")[0],icon_url=user.avatar_url)
        
        embed.set_image(url=bot_msg.attachments[0].url)
        #await ctx.send(file=file)
        await ctx.send(embed=embed)
        

# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(ArtToys(client))

