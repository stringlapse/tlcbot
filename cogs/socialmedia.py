# If a user has the "social media" role they opt in to have their
# art posted from the server to social media. If a message is sent
# in the share art channel a copy of the photo is posted in a mod
# only chat to maybe be put on social media later

import discord
from discord.ext import commands
import datetime
from index import embedsText

shareArtChannel = 728836523214110730
modChannel = 728836900852465716


smRole = 'social media'

class SocialMedia(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Events: make sure to pass in 'self' 
    @commands.Cog.listener()
    async def on_message(self,message):
        if message.channel.id == shareArtChannel:
             for role in message.author.roles:
                if role.name == 'social media' and len(message.attachments) >= 1:
                    embed = embedsText("New image from #share-your-art",'')
                    embed.set_image(url=message.attachments[0].url)
                    embed.set_footer(text=f"{message.author} on {datetime.datetime.now().date()}")
                    await self.client.get_channel(modChannel).send(embed=embed)
            


# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(SocialMedia(client))
