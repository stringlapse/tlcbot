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
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
            await ctx.send(f"You do not have the permissions necessary to be using this command {ctx.message.author.mention}")


    @commands.command()
    @commands.has_role(admin_role)
    async def mute(self,ctx, member: discord.Member, *args):
        channel = self.client.get_channel(int(config('MOD_LOG_CHANNEL')))
        role = discord.utils.get(member.guild.roles, name = mute_role)
        
        if member == ctx.message.author:
            return await ctx.send(f"You can't mute yourself {ctx.message.author.mention}")
        
        if role in member.roles:
            return await ctx.send(f"This user is already currently muted {ctx.message.author.mention}")

        if not args:
            embed = embedsText("User Muted!",f"**{member}** has been muted ")
            embed.set_footer(text=f"Use the {config('PREFIX')}unmute command to unmute this user")
            embedMod = embedsText("User Muted!", f"{ctx.message.author} muted {member} for an unspecified amount of time")
            embedMod.add_field(name='Source',value=f'[Jump!]({ctx.message.jump_url})')
            await channel.send(embed=embedMod)
            await ctx.send(embed=embed)
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
        text = "muted **" + str(member) + "** for", days, p.plural("day",days)+",",hours,p.plural("hour",hours)+", and",minutes,p.plural("minute",minutes)
        if minutes == 0 and hours == 0 and days == 0:
            return await ctx.send(f"Invalid amount of time specified {ctx.message.author.mention}")
        elif days == 0 and hours == 0:
            text = "muted **" + str(member) + "** for", minutes,p.plural("minute",minutes)
        elif days == 0 and minutes == 0:
            text = "muted **" + str(member) + "** for",hours,p.plural("hour",hours)
        elif minutes == 0 and hours == 0:
            text = "muted **" + str(member) + "** for", days, p.plural("day",days)

        text = " ".join(map(str, text))
        embedText = text[0].upper()+text[1:]
        modEmbedText = f"**{ctx.message.author}** {text}"
        
        embed = embedsText("User Muted!",embedText)
        embed.set_footer(text=f"Use the {config('PREFIX')}unmute command to unmute this user sooner")
        embedMod = embedsText("User Muted!", modEmbedText)
        embedMod.add_field(name='Source',value=f'[Jump!]({ctx.message.jump_url})')
        
        await ctx.send(embed=embed)
        modMessage = await channel.send(embed=embedMod)
        await member.add_roles(role)

        await asyncio.sleep(seconds)

        if role in member.roles:
            await member.remove_roles(role)
            embedUnmute = embedsText("User Unmuted!", f"**{member}**\'s timed mute has run out.")
            embedUnmute.add_field(name='Source',value=f'[Jump!]({modMessage.jump_url})')
            await channel.send(embed=embedUnmute)


       
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"The user specified either does not exist or cannot be found {ctx.message.author.mention}")

    @commands.command()
    @commands.has_role(admin_role)
    async def unmute(self,ctx, member: discord.Member):
        role = discord.utils.get(member.guild.roles, name = mute_role)
        if role not in member.roles:
            return await ctx.send(f'This user is not currently muted {ctx.message.author.mention}')
        
        await member.remove_roles(role)
        channel = self.client.get_channel(int(config('MOD_LOG_CHANNEL')))
        
        embedMod=embedsText('User Unmuted!', f'**{member}** was unmuted by **{ctx.message.author}**!')
        embedMod.add_field(name='Source',value=f'[Jump!]({ctx.message.jump_url})')

        embed = embedsText('User Unmuted!', f'**{member}** has been unmuted')
        
        await ctx.send(embed=embed)
        await channel.send(embed=embedMod)
            

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

