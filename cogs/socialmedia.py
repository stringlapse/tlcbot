# If a user has the "social media" role they opt in to have their
# art posted from the server to social media. If a message is sent
# in the share art channel a copy of the photo is posted in a mod
# only chat to maybe be put on social media later

import discord
from discord.ext import commands
import datetime
import re
import sqlite3
import asyncio
import urllib.request
import tweepy
from instabot import Bot
from index import embedsText
from decouple import config
from crop import prepare_and_fix_photo
from urllib.request import urlopen
from discord.utils import get

shareArtChannel = int(config('SHARE_ART_CHANNEL'))
modChannel = int(config('MOD_SOCIAL_ART_GALLERY'))
botID = int(config('BOT_ID'))
smRole = 'social media'


supported_sm = ["twitter","instagram","deviantart","youtube","personal_website"]

bot = commands.Bot(command_prefix=config('PREFIX'))

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
                        footerText = f"{message.author.nick} ({message.author}) on {datetime.datetime.now().date()}"
                        
                        conn = sqlite3.connect('example.db')
                        c = conn.cursor()
                        c.execute("SELECT * from users WHERE user_id=?", (message.author.id,))
                        result = c.fetchone()
                        if result is not None:
                            if len(result[1]):
                                footerText += f"\nTwitter: {result[1]}"
                            if len(result[2]):
                                footerText += f"\nInstagram: {result[2]}"
                            if len(result[3]):
                                footerText += f"\nYoutube: {result[3]}"
                            if len(result[4]):
                                footerText += f"\nDeviantArt: {result[4]}"
                            if len(result[5]):
                                footerText += f"\nPersonal Website: {result[5]}"

                        embed.set_footer(text=footerText)
                        bot_msg = await self.client.get_channel(modChannel).send(embed=embed)

                        # stores message information into database ()
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
                    await self.deleteMessage(bot_msg, result, c)
                elif str(payload.emoji) == "🐦" or str(payload.emoji) == "📷":
                    instagram = bool(str(payload.emoji) == "📷")
                    twitter = bool(str(payload.emoji) == "🐦")
                    check_role = get(bot_msg.guild.roles, name=smRole)
                    optedIn = check_role in payload.member.roles

                    if twitter:
                        await bot_msg.remove_reaction('🐦',payload.member)
                        if int(result[3]) == 1 and optedIn:
                            return await channel.send("This picture has already been posted")
                    else: 
                        await bot_msg.remove_reaction('📷',payload.member)
                        if int(result[4]) == 1 and optedIn:
                            return await channel.send("This picture has already been posted")

                    if not optedIn:
                        return await channel.send(f"User {payload.member} has opted out of TLC social media")

                    try:
                        def check(message):
                            return message.author.id == payload.user_id

                        response = 'n'
                        description = None
                        
                        while response is not 'y':
                            await channel.send("Type the description you would like to post <@" + str(payload.user_id) + ">")
                            description = await self.client.wait_for('message', check=check, timeout=60.0)
                            description = description.content

                            if twitter:
                                while len(description) > 280:
                                    await channel.send(f"<@{str(payload.user_id)}> This tweet ``{description}`` exceeds the 280 character max. Type one with less characters")
                                    description = await self.client.wait_for('message', check=check, timeout=60.0)
                                    description = description.content 

                            await channel.send(f"Posting \"{description}\"\nIs that ok? ``y/n``")
                            response = await self.client.wait_for('message', check=check, timeout=60.0)
                            response = response.content

                            while response is not 'y' and response is not 'n':
                                await channel.send("Fuck you, say 'y' or 'n'")
                                response = await self.client.wait_for('message', check=check, timeout=60.0)
                                response = response.content


                        val = (1, result[0])
                        if instagram:
                            c.execute("UPDATE shared_art SET instagram = ? WHERE bot_message_id = ?", val)
                            await self.postInstagram(url, description, channel)    
                        else: 
                            c.execute("UPDATE shared_art SET twitter = ? WHERE bot_message_id = ?", val)
                            await self.postTwitter(url, description, channel)
                    except asyncio.TimeoutError:
                        await channel.send("<@" + str(payload.user_id) + "> Took to long to respond. Try again.")
                    finally:
                        conn.commit()
                        c.execute("SELECT * FROM shared_art WHERE bot_message_id = ?", (str(payload.message_id),))
                        result2 = c.fetchone()
                        if(int(result2[3]) == 1 and int(result2[4]) == 1):
                            await self.deleteMessage(bot_msg, result2, c)

            conn.commit()
            conn.close()
    
    # DM's user once they add social media role
    @commands.Cog.listener()
    async def on_member_update(self,before,after):
        if len(before.roles) < len(after.roles):
            new_role = next(role for role in after.roles if role not in before.roles)
            if new_role.name in (smRole):
                channel = await after.create_dm()
                platforms = ", ".join(supported_sm)
                text = (
                    f"By adding the {smRole} role you have opted in for having any of your artwork posted on the server (particularly in the finished art channel) shared"
                    f" on TLC's social media. You may opt out simply by removing the role in the role manager channel\n\nIf you would like to have your social media tagged if your" 
                    f" work gets reposted, type the following command in the server ``!set [platform] [name]``. We currently support ``{platforms}``."
                    f" Only do this is you are comfortable with other members knowing your social media, as they will be able to see your account(s) by doing"
                    f" ``!socialmedia`` {after.mention}"
                )
                await channel.send(text)

        elif len(before.roles) > len(after.roles):
            channel = await after.create_dm()
            old_role = next(role for role in before.roles if role not in after.roles)
            if old_role.name in (smRole):
                channel = await after.create_dm()
                platforms = ", ".join(supported_sm)
                text = (
                    f"You just removed the {smRole} role. By doing this none of your posts in the server will be reposted on TLC's social media; you have opted out. Keep in mind"
                    f" that if you previously linked social media using the ``!set`` command users will still be able to see them with ``!socialmedia`` {after.mention}"
                    f" if you would NOT like this to be the case, unlink any social media with ``!unlink [platform]``"
                )
                await channel.send(text)

    # Sends to Twitter from message url
    async def postTwitter(self,url, description, channel):
        try:
            msg = await channel.send("Beginning to post to twitter. May take a couple of minutes.") 
            auth = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'), config('TWITTER_CONSUMER_SECRET')) 
            auth.set_access_token(config('TWITTER_ACCESS_TOKEN'), config('TWITER_ACCESS_SECRET'))
            api = tweepy.API(auth)

            opener = urllib.request.URLopener()
            opener.addheader('User-Agent', 'whatever')
            photo = 'images/post.jpg'
            filename, headers = opener.retrieve(url, photo)

            status = api.update_with_media(photo, description)  
            api.update_status(status = description)
        except Exception as e:
            print(e)
            await channel.send('Could not post. You suck')
        finally:
            await msg.edit(content="Posted! Check twitter to see if everything went well.") 

    # Sends to Instagram from message url
    async def postInstagram(self,url, description, channel):
        try:
            msg = await channel.send("Beginning to post to instagram. May take a couple of minutes.") 
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
        finally:
            await msg.edit(content="Posted! Check instagram to see if everything went well.") 
    
    async def deleteMessage(self, bot_msg, result, c):
        await bot_msg.delete()
        c.execute("DELETE FROM shared_art WHERE bot_message_id =?", (str(result[0]),))

    @bot.command()
    async def set(self,ctx, platform, name):
        if platform.lower() not in supported_sm:
            platforms = ", ".join(supported_sm)
            await ctx.send(f"Platform not yet supported. Choose between ``{platforms}``.\nUsage: {config('PREFIX')}set twitter @TLC_Discord")
            return
        if not name or len(name) == 0:
            await ctx.send(f"Please state your name on the platform.\nUsage: {config('PREFIX')}set twitter @TLC_Discord")
            return
        name = normalize(platform,name)
        author = ctx.message.author.id

        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        val = (author,platform,name)
        c.execute("INSERT OR IGNORE INTO users(user_id,twitter,instagram,personal_website,commission_sheet,youtube,deviantart) VALUES(?,?,?,?,?,?,?)", (author, '','','','','',''))
        c.execute(f"UPDATE users SET {platform}=? WHERE user_id=?",(name,author))
        conn.commit()
        conn.close()

        await ctx.send(f"Set your {platform} name to {name}.")

    # this doesnt do shit yet
    @bot.command() 
    async def unlink(self,ctx, platform):
        if platform.lower() not in supported_sm:
            await ctx.send(f"Only twitter and instagram are supported.\nUsage: {config('PREFIX')}unlink twitter")
            return
        author = ctx.message.author.id
        
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute(f"UPDATE users SET {platform}=? WHERE user_id=?",("",author))
        conn.commit()
        conn.close()
        await ctx.send("Removed your " + platform + " data.")


    @bot.command()
    async def socialmedia(self,ctx,user=None):
        if user == None:
            userid = ctx.message.author.id
        else:
            userid = user[3:-1]

        user = self.client.get_user(int(userid))
        conn = sqlite3.connect('example.db')
        c = conn.cursor()

        c.execute("SELECT * from users WHERE user_id=?", (userid,))
        result = c.fetchone()
        if result == None:
            result = ("","","","","","") # just a workaround for now


        embed = embedsText(f"Social Media for {user}",'')

        embed.set_thumbnail(url=user.avatar_url)
        if len(result[1]):
            embed.add_field(name='<:twitter:742641227622776903> Twitter',value=f"[{result[1]}](http://twitter.com/{result[1][1:]})",inline=False)
        if len(result[2]):
            embed.add_field(name='<:instagram:742641054033117184> Instagram',value=f"[{result[2]}](http://instagram.com/{result[2][1:]})",inline=False)
        if len(result[3]):
            embed.add_field(name='<:youtube:742653485098467399> Youtube',value=f"[{result[3]}](http://youtube.com/c/{result[3][1:]})",inline=False)
        if len(result[4]):
            embed.add_field(name='<:deviantart:742653657228640306> DeviantArt',value=f"[{result[4]}](https://www.deviantart.com/{result[4][1:]})",inline=False)
        if len(result[5]):
            embed.add_field(name='💻 Website',value=f"[{result[5]}]({result[5]})",inline=False)

        if len(embed.fields) == 0:
            embed.description = "This user has no social media linked yet."
        #        await ctx.send(str(result))
        await ctx.send(embed=embed)
        conn.commit()
        conn.close()    

    # twitter and instagram both use the same name format, but in case we add more names, the social media platform 
def normalize(platform,name):
        if name.startswith("@"):
           return name
        elif platform == "personal_website":
            if "https://" not in name:
                return "https://" + name
            return name
        else:
            return "@" + name
           
# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(SocialMedia(client))

