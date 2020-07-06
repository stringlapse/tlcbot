# Commands used for moderation like a mute command go here

import discord
from discord.ext import commands
from index import embedsText
import sqlite3

class Moderation(commands.Cog):
    admin_role = "devs"

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_role(admin_role)
    async def mute(self,ctx, member: discord.Member):
        role = discord.utils.get(member.guild.roles, name = 'muted')
        await member.add_roles(role)
        embed=embedsText('User Muted!', f'**{member}** was muted by **{ctx.message.author}**!')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role(admin_role)
    async def unmute(self,ctx, member: discord.Member):
        role = discord.utils.get(member.guild.roles, name = 'muted')
        if role in member.roles:
            await member.remove_roles(role)
            embed=embedsText('User Unmuted!', f'{member} was unmuted by **{ctx.message.author}**!')
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'**{member}** is not currently muted')
    
    @commands.command()
    @commands.has_role(admin_role)
    async def giveCookie(self,ctx, member: discord.Member, *args):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute(f"SELECT user_id FROM econ WHERE user_id = '{member.id}'")
        if c.fetchone() is None:
            val = (member.user.id, 5)
            c.execute("INSERT INTO econ(user_id ,balance) VALUES(?,?)", val)
            conn.commit()
        c.execute(f"SELECT user_id, balance FROM econ WHERE user_id = '{member.id}'")
        memberBal = int(c.fetchone()[1]) + 1
        val = (memberBal, member.id)
        c.execute("UPDATE econ SET balance = ? WHERE user_id = ?", val)
        conn.commit()
        embed=embedsText(f'Gave {member} :cookie:',f'Reason: {" ".join(args)}')
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Moderation(client))

