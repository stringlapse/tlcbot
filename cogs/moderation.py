# Commands used for moderation like a mute command go here

import discord
from discord.ext import commands
from index import embedsText
from index import admin_role
import sqlite3
import inflect
import re
import asyncio
from decouple import config

mute_role = "Muted"

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_role(admin_role)
    async def mute(self,ctx, member: discord.Member, *args):

        channel = self.client.get_channel(int(config('MOD_LOG_CHANNEL')))
        role = discord.utils.get(member.guild.roles, name = mute_role)

        if member == ctx.message.author:
            return await ctx.send(f"You can't mute yourself {ctx.message.author.mention}")

        if not args:
            await channel.send(f"{ctx.message.author} muted {member} for an unspecified amount of time")
            await ctx.send(f"{member} muted for an unspecified amount of time")
            return await member.add_roles(role)
        
        time = ''.join(args)
        days = re.search('([0-9]+(?=d))',time)
        hours = re.search('([0-9]+(?=h))',time)
        minutes = re.search('([0-9]+(?=m))',time)

        seconds = 0
        if days is not None:
            days = int(days.group(0))
            seconds += days * 24 * 60 * 60
        else:
            days = 0
        
        if hours is not None:
            hours = int(hours.group(0))
            seconds += hours * 60 * 60
        else:
            hours = 0

        if minutes is not None:
            minutes = int(minutes.group(0))
            seconds += minutes * 60
        else:
            minutes = 0

        if minutes > 60:
            hours += minutes//60
            minutes = minutes % 60
        if hours > 24:
            days += hours//24
            hours = hours % 24

        p = inflect.engine()
        text = "muted " + str(member) + " for", days, p.plural("day",days)+",",hours,p.plural("hour",hours)+", and",minutes,p.plural("minute",minutes)
        if minutes == 0 and hours == 0 and days == 0:
            return await ctx.send(f"Invalid amount of time specified {ctx.message.author.mention}")
        elif days == 0 and hours == 0:
            text = "muted " + str(member) + " for", minutes,p.plural("minute",minutes)
        elif days == 0 and minutes == 0:
            text = "muted " + str(member) + " for",hours,p.plural("hour",hours)
        elif minutes == 0 and hours == 0:
            text = "muted " + str(member) + " for", days, p.plural("day",days)
        text = " ".join(map(str, text))
        await ctx.send(text[0].upper()+text[1:])
        await channel.send(str(ctx.message.author) + " " + text)
        await member.add_roles(role)

        await asyncio.sleep(seconds)
        await member.remove_roles(role)


       
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"The user specified either does not exist or cannot be found {ctx.message.author.mention}")

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
    async def clear(self, ctx, amount=1):
        await ctx.channel.purge(limit=amount+1)
        if amount == 1:
            embed=embedsText(f'{amount} message cleared!', '')
        else:
            embed=embedsText(f'{amount} messages cleared!', '')
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Moderation(client))

