# If a user has the "social media" role they opt in to have their
# art posted from the server to social media. If a message is sent
# in the share art channel a copy of the photo is posted in a mod
# only chat to maybe be put on social media later

import discord
from discord.ext import commands
import datetime
import re
import sqlite3
import urllib.request
from instabot import Bot
from index import embedsText
from decouple import config
from crop import prepare_and_fix_photo
from urllib.request import urlopen

shareArtChannel = int(config('SHARE_ART_CHANNEL'))
modChannel = int(config('MOD_SOCIAL_ART_GALLERY'))
botID = int(config('BOT_ID'))
smRole = 'social media'


class SocialMedia(commands.Cog):
    def __init__(self, client):
        self.client = client
    

    # Events: make sure to pass in 'self' 
    @commands.Cog.listener()
    async def on_message(self,message):
        if message.channel.id == shareArtChannel:
             for role in message.author.roles:
                if role.name == 'social media' and len(message.attachments) > 0:
                    for i in range(0, len(message.attachments)):
                        url = message.attachments[i].url
                        embed = embedsText("New image from #share-your-art",'')
                        embed.set_image(url=url)
                        embed.set_footer(text=f"{message.author} on {datetime.datetime.now().date()}")
                        bot_msg = await self.client.get_channel(modChannel).send(embed=embed)

                        # stores message information into database ()
                        conn = sqlite3.connect('example.db')
                        c = conn.cursor()
                        val = (bot_msg.id, message.id, url, 0, 0)
                        c.execute("INSERT INTO shared_art(bot_message_id,original_message_id,image_url,twitter,instagram) VALUES(?,?,?,?,?)", val)
                        conn.commit()
                        conn.close()

                        await bot_msg.add_reaction('🐦')
                        await bot_msg.add_reaction('📷')
                        await bot_msg.add_reaction('❌')
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        if payload.channel_id == modChannel and payload.user_id != botID:
            channel =  self.client.get_channel(modChannel)
            conn = sqlite3.connect('example.db')
            c = conn.cursor()
            c.execute("SELECT * FROM shared_art WHERE bot_message_id = ?", (str(payload.message_id),))
            result = c.fetchone()

            if result is not None:
                bot_msg = await channel.fetch_message(result[0])
                url = result[2]
                if str(payload.emoji) == "❌":
                    await bot_msg.delete()
                    c.execute("DELETE FROM shared_art WHERE bot_message_id =?", (str(result[0]),))
                elif str(payload.emoji) == "🐦":
                    await bot_msg.remove_reaction('🐦',payload.member)
                    await channel.send("this would work if twitter ACTUALLY ACCEPTED OUR APPLICATION")
                elif str(payload.emoji) == "📷":
                    await bot_msg.remove_reaction('📷',payload.member)
                    if int(result[4]) == 1:
                        return await channel.send("this picture has already been posted to instagram")

                    def check(message):
                        return message.author.id == payload.user_id

                    response = 'n'
                    description = None 
                    while response is not 'y':
                        await channel.send("Type the description you would like to post")
                        description = await self.client.wait_for('message', check=check, timeout=60.0)
                        description = description.content
                        await channel.send(f"Posting \"{description}\"\nIs that ok? ``y/n``")
                        response = await self.client.wait_for('message', check=check, timeout=60.0)
                        response = response.content

                    val = (1, result[0])
                    c.execute("UPDATE shared_art SET instagram = ? WHERE bot_message_id = ?", val)

                    await self.postInstagram(url, description, channel)    
                    await channel.send("Posted to instagram :)") 
                    
                conn.commit()
                conn.close()
                    



    # Sends to Twitter from message url
    @commands.command()
    async def postTwitter(self,ctx,url):
        try:
            m = re.findall('\d[0-9]+',url)
            channelID = int(m[1])
            msgID = int(m[2])
            msg  = await self.client.get_channel(channelID).fetch_message(msgID)
            await ctx.send(msg.attachments[0].url) 
        except Exception as e:
            print(e)
            await ctx.send('Could not post. You suck')

    # Sends to Instagram from message url
    async def postInstagram(self,url, description, channel):
        try:
            opener = urllib.request.URLopener()
            opener.addheader('User-Agent', 'whatever')
            photo = 'images/post.jpg'
            filename, headers = opener.retrieve(url, photo)

            bot = Bot()
            bot.login(username=config('INSTAGRAM_USERNAME'),
                        password=config('INSTAGRAM_PASSWORD'))

            prepare_and_fix_photo(photo)
            bot.upload_photo(photo, 
                    caption = description)
        
        except Exception as e:
            print(e)
        
    
# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(SocialMedia(client))

