import discord
from discord.ext import commands
from index import admin_role
from decouple import config
import sqlite3
import re
from index import embedsText

class Cookies(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        invites = await self.getsInvites()
        for invite in invites:
            c.execute(f"SELECT * FROM invites WHERE invite_id =?",(invite.id,))
            result = c.fetchone()
            if result is None:
                c.execute(f"INSERT INTO invites(invite_id, uses) VALUES(?,?)",(invite.id,invite.uses))
            else:
                if invite.uses != result[1]:
                    c.execute(f"UPDATE invites SET uses = ? WHERE invite_id = ?",(invite.uses, invite.id))
            conn.commit()
        conn.close()
    
    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute(f"INSERT INTO invites(invite_id, uses) VALUES(?,?)",(invite.id,invite.uses))
        conn.commit()
        conn.close()
    
    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute(f"SELECT * FROM invites WHERE invite_id =?",(invite.id,))
        result = c.fetchone()
        if result is not None:
            c.execute("DELETE FROM invites WHERE invite_id =?", (str(result[0]),))
        conn.commit()
        conn.close()
    
    @commands.command()
    @commands.has_role(admin_role)
    async def givecookie(self,ctx, member: discord.Member, *args):
        if member == ctx.message.author:
            return await ctx.send("You can't give yourself a cookie silly")
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute(f"SELECT user_id FROM econ WHERE user_id = '{member.id}'")
        if c.fetchone() is None:
            val = (member.id, 0)
            c.execute("INSERT INTO econ(user_id ,balance) VALUES(?,?)", val)
            conn.commit()
        c.execute(f"SELECT user_id, balance FROM econ WHERE user_id = '{member.id}'")
        memberBal = int(c.fetchone()[1]) + 1
        val = (memberBal, member.id)
        c.execute("UPDATE econ SET balance = ? WHERE user_id = ?", val)
        conn.commit()
        reason = "None"
        if len(args) > 0:
            reason = " ".join(args)
        embed=embedsText(f'Gave {member} :cookie:',f'Reason: {reason}')
        await ctx.send(embed=embed)

    # Gives a cookie to the person who invited user 
    @commands.Cog.listener()
    async def on_member_join(self,member):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        invites = await self.getsInvites()
        for invite in invites:
            c.execute(f"SELECT * FROM invites WHERE invite_id =?",(invite.id,))
            result = c.fetchone()
            if result is not None:
                if invite.uses > int(result[1]):
                    if not (invite.inviter.bot):
                        userID = invite.inviter.id
                        c.execute(f"SELECT * FROM econ WHERE user_id = ? ",(userID,))
                        result = c.fetchone()
                        if result is None:
                            c.execute("INSERT INTO econ(user_id ,balance) VALUES(?,?)", (userID,1))
                        else:
                            memberBal = int(result[1]) + 1
                            val = (memberBal, userID)
                            c.execute("UPDATE econ SET balance = ? WHERE user_id = ?", val)
                        conn.commit()
                        channel = await self.client.fetch_channel(int(config("GENERAL_ONE_CHANNEL_ID")))
                        await channel.send(f"<@{userID}> Thanks for inviting <@{member.id}> to the server. Have a :cookie:")
                    c.execute("UPDATE invites set uses = ? WHERE invite_id = ?", (invite.uses,invite.id))
                    break

    # awards cookie when someone bumped disboard
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == int(config('DISBOARD_ID')):
            if self.check_all_message("Bump done :thumbsup:", message):
                m = re.search(r'<@!?(\d+)>', message.embeds[0].description)
                tag = m.group(0)
                member = tag
                member = member[2:member.find('>')]
                conn = sqlite3.connect('example.db')
                c = conn.cursor()
                c.execute(f"SELECT user_id FROM econ WHERE user_id = '{member}'")
                if c.fetchone() is None:
                    val = (member, 1)
                    c.execute("INSERT INTO econ(user_id ,balance) VALUES(?,?)", val)
                    conn.commit()
                c.execute(f"SELECT user_id, balance FROM econ WHERE user_id = '{member}'")
                memberBal = int(c.fetchone()[1]) + 1
                val = (memberBal, member)
                c.execute("UPDATE econ SET balance = ? WHERE user_id = ?", val)
                conn.commit()
                channel = message.channel
                await channel.send(f"Thanks for bumping {tag} have a :cookie:")
         
    # simulates disboard's bump message
    @commands.command()
    @commands.has_role(admin_role)
    async def bumpYes(self, ctx):
        embed = discord.Embed(title="DISBOARD: The Public Server List", 
                            url="https://disboard.org/",
                            description=f"{ctx.author.mention}\nBump done :thumbsup:\nCheck it on DISBOARD: https://disboard.org/")

        embed.set_image(url="https://disboard.org/images/bot-command-image-bump.png")
        await ctx.send(embed=embed)
    
    # simulates disboard's bump fail message
    @commands.command()
    @commands.has_role(admin_role)
    async def bumpNo(self, ctx):
        embed = discord.Embed(title="DISBOARD: The Public Server List", 
                            url="https://disboard.org/",
                            description=f"{ctx.author.mention}, Please wait another 97 minutes until the server can be bumped")

        embed.set_thumbnail(url="https://disboard.org/images/bot-command-image-thumbnail-error.png")
        await ctx.send(embed=embed)

    # allows user to check their own or another user's balance
    @commands.command(pass_context = True , aliases=['cookie', 'cookies'])
    async def balance(self, ctx, member:discord.Member=None):
        memberID = ctx.author.id
        name = ctx.author
        if member is not None:
            memberID = member.id
            name = member
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute(f"SELECT user_id FROM econ WHERE user_id = '{memberID}'")
        noUser = c.fetchone() is None
        if noUser:
            val = (memberID, 0)
            c.execute("INSERT INTO econ(user_id ,balance) VALUES(?,?)", val)
            conn.commit()
        c.execute(f"SELECT user_id, balance FROM econ WHERE user_id = '{memberID}'")
        result = c.fetchone()
        bal = int(result[1])
        embed=embedsText(f'{name}\'s balance: {bal} :cookie:','')
        await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        i = 1
        string = ''
        for row in c.execute("SELECT * FROM econ ORDER BY balance DESC"):
            balance = int(row[1])
            if balance > 0:
                user = await self.client.fetch_user(int(row[0])) 
                string += f'\n#{i}: **{balance}** :cookie: \t{user}'
                i += 1
            if i > 10:
                break
        embed=embedsText('TLC Leaderboard', f'{string}')                                                              
        await ctx.send(embed=embed)
   
    def check_all_message(self,check_for, message):
        try:
            if check_for in message.content:
                return True
            for e in message.embeds:
                if any(item and check_for in item for item in (e.title, e.footer, e.description)):
                    return True
                if e.fields:
                    for field in e.fields:
                        if check_for in field.name or check_for in field.value:
                            return True
            return False
        except TypeError:
            pass

    async def getsInvites(self):
        guild = self.client.get_guild(int(config('GUILD_ID')))
        invites = await guild.invites()
        return invites
    
# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Cookies(client))

