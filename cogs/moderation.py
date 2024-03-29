# Commands used for moderation like a mute command go here

import discord
from discord.ext import commands
from index import embedsText
from index import admin_role
import sqlite3

mute_role = "Muted"

class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Invite logging: cookies.py looks at what invite new joins used to award cookies,
    # but that's also a useful function for moderation. Mixed in with the invite cookies
    # system, the bot sends a message to the mod log when an invite is used. This is helpful
    # for situations like raids when you want to see what invite people are using so you can
    # delete it. I would make it a function here that gets called by cookies.py but for
    # something that I expect to only be one or two lines I don't think it's really worth it.

    @commands.command()
    @commands.has_role(admin_role)
    async def mute(self,ctx, member: discord.Member):
        if member == ctx.message.author:
            await ctx.send("You can't mute yourself")
            return
        role = discord.utils.get(member.guild.roles, name = mute_role)
        if role not in member.roles:
            await member.add_roles(role)
            embed=embedsText('User Muted!', f'**{member}** was muted by **{ctx.message.author}**!')
            await ctx.send(embed=embed)
            await ctx.message.delete()
        else:
            #await ctx.send(f'**{member}** is already muted')
            embed=embedsText(f'**{member}** is already muted', '')
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role(admin_role)
    async def unmute(self,ctx, member: discord.Member):
        role = discord.utils.get(member.guild.roles, name = mute_role)
        if role in member.roles:
            await member.remove_roles(role)
            embed=embedsText('User Unmuted!', f'**{member}** was unmuted by **{ctx.message.author}**!')
            await ctx.send(embed=embed)
            await ctx.message.delete()
        else:
            #await ctx.send(f'**{member}** is not currently muted')
            embed=embedsText(f'**{member}** is not currently muted', '')
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role(admin_role)
    async def clear(self, ctx, amount=1):
        await ctx.channel.purge(limit=amount+1)
        if amount == 1:
            embed=embedsText(f'{amount} message cleared!', '')
        else:
            embed=embedsText(f'{amount} messages cleared!', '')
        await ctx.send(embed=embed, delete_after=5)

def setup(client):
    client.add_cog(Moderation(client))

