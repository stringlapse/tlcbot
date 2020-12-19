# Commands used for moderation like a mute command go here

import discord
from discord.ext import commands
from index import embedsText
from index import admin_role
import sqlite3
import inflect

mute_role = "Muted"

class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_role(admin_role)
    async def mute(self,ctx, member: discord.Member):
        if member == ctx.message.author:
            await ctx.send("You can't mute yourself")
            return
        role = discord.utils.get(member.guild.roles, name = mute_role)
        await member.add_roles(role)
        embed=embedsText('User Muted!', f'**{member}** was muted by **{ctx.message.author}**!')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role(admin_role)
    async def unmute(self,ctx, member: discord.Member):
        role = discord.utils.get(member.guild.roles, name = mute_role)
        if role in member.roles:
            await member.remove_roles(role)
            embed=embedsText('User Unmuted!', f'**{member}** was unmuted by **{ctx.message.author}**!')
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'**{member}** is not currently muted')
    
    @commands.command()
    @commands.has_role(admin_role)
    async def numrole(self,ctx,*args):
        roleName = " ".join(args)

        role = None
        for r in ctx.guild.roles:
            if r.name.lower() == roleName.lower():
                role = r

        if role is None:
            return await ctx.send(f"The role specified does not exist. {ctx.message.author.mention}")

        num = 0
        for member in ctx.guild.members:
             if role in member.roles:
                 num += 1
        
        p = inflect.engine()
        text = "There",p.plural_verb("is",num),num,p.plural("person",num) + " with the **" + role.name + "** role " + ctx.message.author.mention
        text = " ".join(map(str, text))
        await ctx.send(text)
                 


    @commands.command()
    @commands.has_role(admin_role)
    async def clear(self, ctx, amount=1):
        await ctx.channel.purge(limit=amount+1)
        if amount == 1:
            embed=embedsText(f'{amount} message cleared!', '')
        else:
            embed=embedsText(f'{amount} messages cleared!', '')
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Moderation(client))

