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
import os
from instabot import Bot
from index import embedsText
from decouple import config
from PIL import Image
import PIL
import glob
from crop import prepare_and_fix_photo
from urllib.request import urlopen
from discord.utils import get

shareArtChannels = config('SHARE_ART_CHANNEL')
modChannel = int(config('MOD_SOCIAL_ART_GALLERY'))
botID = int(config('BOT_ID'))
smRole = 'Share Me'


supported_sm = ["twitter","instagram","deviantart","youtube","personal_website","artstation","twitch","tiktok"]
supported_platforms_list = "Instagram, Twitter, YouTube, ArtStation, DeviantArt, TikTok, Twitch, and Personal Website (use `personal_website` for platform)"

bot = commands.Bot(command_prefix=config('PREFIX'))

class SocialMedia(commands.Cog):
    def __init__(self, client):
        self.client = client
    

    # Events: make sure to pass in 'self' 
    @commands.Cog.listener()
    async def on_message(self,message):
        if str(message.channel.id) in shareArtChannels:
             for role in message.author.roles:
                if role.name == smRole and len(message.attachments) > 0:
                    for i in range(0, len(message.attachments)):
                        image = message.attachments[i]
                        halalExtensions = ['.png','.jpg','.jpeg','.gif']
                        if any(s in image.filename for s in halalExtensions): 
                            instaHalal = True
                            if '.gif' in image.filename:
                                instaHalal = False
                            url = image.url
                            embed = discord.Embed(description=message.content,color=int(config("EMBED_COLOR"), 16))
                            embed.set_author(name=message.author.display_name,icon_url=message.author.avatar_url)
                            embed.add_field(name=f'Source: #{message.channel.name}',value=f'[Jump!]({message.jump_url})')

                            #embed = embedsText(f"New image from #{message.channel.name}", f'**Source**\n[Jump!]({message.jump_url})')
                            embed.set_image(url=url)
                            footerText = f"{message.author.display_name} ({message.author}) on {datetime.datetime.now().date()}"
                            
                            conn = sqlite3.connect('example.db')
                            c = conn.cursor()
                            c.execute("SELECT * from users WHERE user_id=?", (message.author.id,))
                            result = c.fetchone()
                            if result is not None:

                                # Escape any markdown characters in usernames
                                filteredResult = []
                                for item in result:
                                    filteredResult.append(cleanMarkdown(item))

                                if result[2] != None:
                                    if len(result[2]):
                                        footerText += f"\nInstagram: {filteredResult[2]}"
                                if result[1] != None:
                                    if len(result[1]):
                                        footerText += f"\nTwitter: {filteredResult[1]}"
                                if result[3] != None:
                                    if len(result[3]):
                                        footerText += f"\nYouTube: {filteredResult[3]}"
                                if result[6] != None:
                                    if len(result[6]):
                                        footerText += f"\nArtStation: {filteredResult[6]}"
                                if result[4] != None:
                                    if len(result[4]):
                                        footerText += f"\nDeviantArt: {filteredResult[4]}"
                                if result[8] != None:
                                    if len(result[8]):
                                        footerText += f"\nTikTok: {filteredResult[8]}"
                                if result[7] != None:
                                    if len(result[7]):
                                        footerText += f"\nTwitch: {filteredResult[7]}"
                                if result[5] != None:
                                    if len(result[5]):
                                        footerText += f"\nPersonal Website: {filteredResult[5]}"

                            embed.set_footer(text=footerText)
                            bot_msg = await self.client.get_channel(modChannel).send(embed=embed)
                            # stores message information into database ()
                            val = (bot_msg.id, message.id, url, 0, 1)
                            if instaHalal:
                                await bot_msg.add_reaction('📷')
                                val = (bot_msg.id, message.id, url, 0, 0)
                            
                            c.execute("INSERT INTO shared_art(bot_message_id,original_message_id, image_url,twitter,instagram) VALUES(?,?,?,?,?)", val)
                            conn.commit()
                            conn.close()

                            await bot_msg.add_reaction('🐦')
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

                    photo = 'images/post.jpg'
                    if os.path.exists(photo):
                        os.remove(photo)
                    if os.path.exists("images/post.jpg.REMOVE_ME"):
                        os.remove("images/post.jpg.REMOVE_ME")

                    opener = urllib.request.URLopener()
                    opener.addheader('User-Agent', 'whatever')
                    filename, headers = opener.retrieve(url, photo)

                    if twitter:
                        await bot_msg.remove_reaction('🐦',payload.member)
                        if int(result[3]) == 1:
                            return await channel.send("This picture has already been posted")
                        
                        size = os.stat(photo).st_size 
                        while size > 3072000: # compression algorithm for twitter
                            picture = Image.open(photo)
                            try:
                                if picture.is_animated:
                                    return await channel.send(f"This gif at {round(size/1000)}kb is bigger than the 3072kb max allowed by twitter and can not be posted. The devs are working on supporting large gifs.")
                            except AttributeError:
                                pass
                            if picture.mode == "RGBA": 
                                # trans rights!
                                background = Image.new('RGB', picture.size, (255, 255, 255))
                                background.paste(picture, (0,0), picture)
                                background.save(photo)
                            picture = Image.open(photo)
                            picture.save(photo, optimize=True, quality=30) 
                            size2 = os.stat(photo).st_size
                            print(f"Was around {size/1000} kb, compressed to {size2/1000}kb")
                            size = size2

                    else: 
                        await bot_msg.remove_reaction('📷',payload.member)
                        if int(result[4]) == 1:
                            return await channel.send("This picture has already been posted")

                    if not optedIn:
                        return await channel.send(f"User {payload.member} has opted out of TLC social media")

                    try:
                        def check(message):
                            return message.author.id == payload.user_id and message.channel.id == modChannel

                        response = 'n'
                        description = None
                        
                        while response != 'y':
                            msg = await channel.send("Type the description you would like to post. Because discord uses the **@** character to also ping users use the **%%** in place of that. For example, **%%AdamSandler** instead of **@AdamSandler**. Use **&&** in place of **#**. Type only ``q`` to quit <@" + str(payload.user_id) + ">")
                            description = await self.client.wait_for('message', check=check, timeout=120.0)
                            #print("description: ")
                            #print(description.content)
                            channel_re = re.compile(r'<#([0-9]+)>')
                            mention_re = re.compile(r'<@!([0-9]+)>')
                            for mention in re.findall(mention_re, description.content):
                                user_name = self.client.get_user(int(mention))
                                description.content = description.content.replace("<@!" + mention + ">","@" + str(user_name).split("#")[0])
                            for hashtag in re.findall(channel_re, description.content):
                                channel_name = self.client.get_channel(int(hashtag))
                                description.content = description.content.replace("<#" + hashtag + ">","#" + str(channel_name))
                            description = description.content
                            # print(description)
                            if description == 'q':
                                await msg.delete()
                                break

                            description = description.replace("%%","@")
                            description = description.replace("&&","#")
                            if twitter:
                                while len(description) > 280:
                                    await channel.send(f"<@{str(payload.user_id)}> This tweet ``{description}`` exceeds the 280 character max. Type one with less characters")
                                    description = await self.client.wait_for('message', check=check, timeout=60.0)
                                    description = description.content
                                    description = description.replace("%%","@")
                                    description = description.replace("&&","#")

                            if instagram:
                                while description.count('#') > 30:
                                    await channel.send(f"Instagram limits posts to 30 tags and you used {description.count('#')}. Please type a description with 30 tags maximum.")
                                    description = await self.client.wait_for('message', check=check, timeout=60.0)
                                    description = description.content
                                    description = description.replace("%%","@")
                                    description = description.replace("&&","#")

                            await channel.send(f"Posting \"{description}\"\nIs that ok? ``y/n``")
                            response = await self.client.wait_for('message', check=check, timeout=60.0)
                            response = response.content

                            while response != 'y' and response != 'n':
                                await channel.send("Fuck you, say 'y' or 'n'")
                                response = await self.client.wait_for('message', check=check, timeout=60.0)
                                response = response.content
    
                        if instagram:
                            img = Image.open(photo, 'r')  
                            if img.mode == "RGBA": 
                                # trans rights!
                                background = Image.new('RGB', img.size, (255, 255, 255))
                                background.paste(img, (0,0), img)
                                background.save(photo)

                        val = (1, result[0])
                        if instagram and description != 'q':
                            await self.postInstagram(photo,description, channel,c,val)
                            conn.commit()
                        if twitter and description != 'q': 
                            await self.postTwitter(photo,description, channel,c,val)
                            conn.commit()
                    except asyncio.TimeoutError:
                        await channel.send("<@" + str(payload.user_id) + "> Took too long to respond. Try again.")
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
                if after.dm_channel == None:
                    channel = await after.create_dm()
                else:
                    channel = after.dm_channel
                platforms = ", ".join(supported_sm)
                text = (
                    f"By adding the {smRole} role you have opted in for having any of your artwork posted on the server (particularly in the finished art channel) shared"
                    f" on TLC's social media. You may opt out simply by removing the role in the role manager channel\n\nIf you would like to have your social media tagged if your" 
                    f" work gets reposted, type the following command in the server: ``{config('PREFIX')}link [platform] [name]``. We currently support ``{platforms}``."
                    f" Only do this if you are comfortable with other members knowing your social media, as they will be able to see your account(s) by doing"
                    f" ``{config('PREFIX')}socialmedia @{after.display_name}``."
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
                    f" that if you previously linked social media using the ``{config('PREFIX')}link`` command users will still be able to see them with ``{config('PREFIX')}socialmedia @{after.display_name}``."
                    f" if you would NOT like this to be the case, unlink any social media with ``{config('PREFIX')}unlink [platform]``."
                )
                await channel.send(text)

    # Sends to Twitter from message url
    async def postTwitter(self,photo,description, channel,c,val):
        try:
            msg = await channel.send("Beginning to post to twitter. May take a couple of minutes.") 
            auth = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'), config('TWITTER_CONSUMER_SECRET')) 
            auth.set_access_token(config('TWITTER_ACCESS_TOKEN'), config('TWITER_ACCESS_SECRET'))
            api = tweepy.API(auth)
            status = api.update_with_media(photo, description)  
        except Exception as e:
            print(e)
            await msg.edit(content='Something went wrong. The error has been sent to our dev team. Notify them for assistance.')
        else:
            await msg.edit(content="Posted! Check Twitter to see if everything went well. <https://twitter.com/tlc_discord>")
            await channel.send("Link to post: " + status.entities["media"][0]["url"])
            c.execute("UPDATE shared_art SET twitter = ? WHERE bot_message_id = ?", val)

    # Sends to Instagram from message url
    async def postInstagram(self,photo,description,channel,c,val):
        try:
            msg = await channel.send("Beginning to post to instagram. May take a couple of minutes.") 
            bot = Bot()
            bot.login(username=config('INSTAGRAM_USERNAME'),
                        password=config('INSTAGRAM_PASSWORD'))

            prepare_and_fix_photo(photo)
            bot.upload_photo(photo, 
                    caption = description)
        except Exception as e:
            print(e)
            await msg.edit(content="Something went wrong. The error has been sent to our dev team. Notify them for assistance.")
        except SystemExit:
            print("Instagram posting failed, catching SystemExit and notifying user")
            await msg.edit(content="Posting failed. Check if the Instagram account is locked.")
        else:
            await msg.edit(content=f"Posted! Check Instagram to see if everything went well. <https://instagram.com/{config('INSTAGRAM_USERNAME')}>")
            c.execute("UPDATE shared_art SET instagram = ? WHERE bot_message_id = ?", val)
    
    async def deleteMessage(self, bot_msg, result, c):
        await bot_msg.delete()
        c.execute("DELETE FROM shared_art WHERE bot_message_id =?", (str(result[0]),))

    @bot.command()
    async def link(self,ctx, platform="", name=""):
        # Prevent people from setting their name to "everyone" to prevent people from abusing the bot to ping @everyone
        if name.lower() == "everyone" or name.lower() == "@everyone":
            await ctx.send("You can't set your name to \"everyone\"")
            return

        if name.lower() == "tlc_discord" or name.lower() == "@tlc_discord":
            await ctx.send("That's our username, use your own instead")
            return

        if ctx.message.mentions:
            await ctx.send("You seem to have pinged someone. Try the same command without the @")
            return

        if name.startswith('@'):
            name = name[1:]

        platforms = supported_platforms_list
        if platform == "":
            await ctx.send(f"Please specify a platform. Currently supported platforms are {platforms}.\nExample: `{config('PREFIX')}link twitter TLC_Discord`")
            return
        else:
            if platform.lower() not in supported_sm:
                await ctx.send(f"Platform not yet supported. Choose between {platforms}.\nExample: `{config('PREFIX')}link twitter TLC_Discord`")
                return
            if name == "":
                await ctx.send(f"Please state your name on the platform.\nExample: `{config('PREFIX')}link twitter TLC_Discord`")
                return
            if not name or len(name) == 0:
                await ctx.send(f"Please state your name on the platform.\nExample: `{config('PREFIX')}link twitter TLC_Discord`")
                return
            name = normalize(platform.lower(),name)
            author = ctx.message.author.id

            conn = sqlite3.connect('example.db')
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO users(user_id,twitter,instagram,personal_website,youtube,deviantart,artstation,twitch,tiktok) VALUES(?,?,?,?,?,?,?,?,?)", (author, '','','','','','','',''))
            c.execute(f"UPDATE users SET {platform.lower()}=? WHERE user_id=?",(name,author)) # Using user input in a SQL query is usually a bad idea but we only get to this point if the input is in our supported_sm list so SQL injection shouldn't be possible
            conn.commit()
            conn.close()

            if platform.lower() == "personal_website":
                embed = discord.Embed(title=f"Set your personal website to {cleanMarkdown(name)}.", color=int(config("EMBED_COLOR"), 16))
                await ctx.send(embed=embed)
            elif platform.lower() == "youtube":
                embed = discord.Embed(title=f"Set your YouTube channel to {cleanMarkdown(name)}.", color=int(config("EMBED_COLOR"), 16))
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title=f"Set your {platform} name to {cleanMarkdown(name)}.", color=int(config("EMBED_COLOR"), 16))
                await ctx.send(embed=embed)

    @bot.command() 
    async def unlink(self,ctx, platform=""):
        platforms = supported_platforms_list
        if platform == "":
            await ctx.send(f"Please specify a platform. Currently supported platforms are {platforms}.\nExample: `{config('PREFIX')}link twitter TLC_Discord`")
            return
        if platform.lower() not in supported_sm:
            await ctx.send(f"Only {platforms} are supported.\nExample: ``{config('PREFIX')}unlink twitter``")
            return
        author = ctx.message.author.id
        
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute(f"UPDATE users SET {platform.lower()}=? WHERE user_id=?",("",author)) # Using user input in a SQL query is usually a bad idea but we only get to this point if the input is in our supported_sm list so SQL injection shouldn't be possible
        conn.commit()
        conn.close()
        embed = discord.Embed(title=f"Removed your {platform} data.", color=int(config("EMBED_COLOR"), 16))
        await ctx.send(embed=embed)


    @bot.command(aliases=['sm'])
    async def socialmedia(self,ctx,*user):
        user = ' '.join(user)
        # no user argument, just lookup self
        if not user:
            userid = ctx.message.author.id
            user = self.client.get_user(int(userid))
        
        # ping argument or name
        #elif user.startswith("<@!"):
        #    userid = user[3:-1]
        #    user = self.client.get_user(int(userid))
        elif ctx.message.mentions:
            user = ctx.message.mentions[0]
            userid = user.id
        else:
            user = ctx.guild.get_member_named(user)
            if user != None:
                userid = user.id 
        if (user == None):
            await ctx.send("No matching user could be found. Either mention them, type their nickname (exact match), or their unique discord tag.")
            return
        
        conn = sqlite3.connect('example.db')
        c = conn.cursor()

        c.execute("SELECT * from users WHERE user_id=?", (userid,))
        result = c.fetchone()
        if result == None:
            result = ("","","","","","","","","") # just a workaround for now

        embed = embedsText(f"{ctx.message.guild.get_member(int(userid)).display_name}'s social media",'')

        embed.set_thumbnail(url=user.avatar_url)

        # Escape any markdown characters in usernames
        filteredResult = []
        for item in result:
            filteredResult.append(cleanMarkdown(item))

        if result[2] != None:
            if len(result[2]):
                embed.add_field(name='<:instagram:746822890657153025> Instagram',value=f"[{filteredResult[2]}](http://instagram.com/{result[2][1:]})",inline=False)
        if result[1] != None:
            if len(result[1]):
                embed.add_field(name='<:twitter:852398421620424704> Twitter',value=f"[{filteredResult[1]}](http://twitter.com/{result[1][1:]})",inline=False)
        if result[3] != None:
            if len(result[3]):
                embed.add_field(name='<:youtube:852404377171001354> YouTube',value=f"[Channel]({filteredResult[3]})",inline=False)
        if result[6] != None:
            if len(result[6]):
                embed.add_field(name='<:artstation:852405321824993290> ArtStation',value=f"[{filteredResult[6]}](http://artstation.com/{result[6][1:]})",inline=False)
        if result[4] != None:
            if len(result[4]):
                embed.add_field(name='<:deviantart:852401746495012874> DeviantArt',value=f"[{filteredResult[4]}](https://www.deviantart.com/{result[4][1:]})",inline=False)
        if result[8] != None:
            if len(result[8]):
                embed.add_field(name='<:tiktok:852400600947490826> TikTok',value=f"[{filteredResult[8]}](https://www.tiktok.com/{result[8]})",inline=False)
        if result[7] != None:
            if len(result[7]):
                embed.add_field(name='<:twitch:852402994138185749> Twitch',value=f"[{filteredResult[7]}](https://www.twitch.tv/{result[7][1:]})",inline=False)
        if result[5] != None:
            if len(result[5]):
                embed.add_field(name='💻 Website',value=f"[{filteredResult[5]}]({result[5]})",inline=False)
        

        if len(embed.fields) == 0:
            embed.description = "This user has no social media linked yet."
        #        await ctx.send(str(result))
        embed.set_footer(text=user)
        await ctx.send(embed=embed)
        conn.commit()
        conn.close()    

    # twitter and instagram both use the same name format, but in case we add more names, the social media platform 
def normalize(platform,name):
        if name.startswith("@"):
           return name
        elif platform == "personal_website" or platform == "youtube":
            if "https://" not in name:
                return "https://" + name
            return name
        else:
            return "@" + name

# Escapes markdown characters in a string
def cleanMarkdown(text):
    if type(text) == str:
        text = text.replace('_', "\_")
        text = text.replace('*', "\*")
        text = text.replace('~', "\~")
    return text

# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(SocialMedia(client))

