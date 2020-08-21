# An example of how a Cog should be properly instantiated

import discord
from discord.ext import commands
from decouple import config
import sqlite3
from datetime import date

starboardID = int(config('STARBOARD_CHANNEL_ID'))
recognizedEmojis = ['⭐']
minimumEmoji = 2

class Starboard(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_reaction_add(self,reaction,user):
        starboard = self.client.get_channel(starboardID)
        count = reaction.count
        if reaction.message.channel.id != starboardID:
            if reaction.emoji in recognizedEmojis and count >= minimumEmoji:
                conn = sqlite3.connect('example.db')
                c = conn.cursor()
                c.execute('SELECT * FROM starboard WHERE message_id = ?',(reaction.message.id,))
                result = c.fetchone()
                message = f'{reaction.emoji} **{count}** {reaction.message.channel.mention}'
                if result is None:
                    embed = discord.Embed(description=reaction.message.content,color=0x228B22)
                    embed.set_author(name=reaction.message.author.display_name,icon_url=reaction.message.author.avatar_url)
                    embed.add_field(name='**Source**',value=f'[Jump!]({reaction.message.jump_url})')
                    if(len(reaction.message.attachments) > 0):
                        embed.set_image(url=reaction.message.attachments[0].url)
                    currentDate = date.today()
                    today = currentDate.strftime('%m/%d/%Y').replace("/0", "/")
                    if today[0] == '0':
                        today = today[1:]
                    embed.set_footer(text=f'{reaction.message.id} • {today}')
                    sent_msg = await starboard.send(content=message,embed=embed)
                    
                    c.execute('INSERT INTO starboard(message_id,bot_message_id) VALUES(?,?)',(reaction.message.id,sent_msg.id))
                    conn.commit()
                else:
                    emoji = '⭐'
                    if count >= 5:
                        emoji = '🌟'
                    if count >= 10:
                        emoji = '💫'
                    message = f'{emoji} **{count}** {reaction.message.channel.mention}'
                    bot_msg = await starboard.fetch_message(int(result[1]))
                    await bot_msg.edit(content=message)
    
    @commands.Cog.listener()
    async def on_reaction_remove(self,reaction,user):
        starboard = self.client.get_channel(starboardID)
        if reaction.emoji in recognizedEmojis:
            conn = sqlite3.connect('example.db')
            c = conn.cursor()
            c.execute('SELECT * FROM starboard WHERE message_id = ?',(reaction.message.id,))
            result = c.fetchone()
            if result is not None:
                message = f'{reaction.emoji}**{reaction.count}**{reaction.message.channel.mention}'
                bot_msg = await starboard.fetch_message(int(result[1]))
                await bot_msg.edit(content=message)
    
# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Starboard(client))
