import discord
import time 
from datetime import datetime, date, time, timedelta, timezone
from discord.ext import commands
from index import admin_role
from decouple import config
import sqlite3
import asyncio
import re
from index import embedsText
from datetime import date

announcementsID = int(config('ANNOUNCEMENTS_CHANNEL_ID'))
botID = int(config('BOT_ID'))
startingCookies = 0
rewards = dict(
    bump= 1,
    invite= 3,
    modGift= 5
)

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
                c.execute(f"INSERT INTO invites(invite_id,uses) VALUES(?,?)",(invite.id,invite.uses))
            else:
                if invite.uses != result[1]:
                    c.execute(f"UPDATE invites SET uses = ? WHERE invite_id = ?",(invite.uses, invite.id))
            conn.commit()
        conn.close()
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        userID = payload.user_id
        if userID != botID:
            messageID = payload.message_id
            conn = sqlite3.connect('example.db')
            c = conn.cursor()
            c.execute("SELECT * FROM event WHERE message_id =?",(messageID,))
            result = c.fetchone()
            if result is not None:
                claimedID = result[3]
                endDate = float(result[2])
                cookies = int(result[1])
                today = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
                if today > endDate:
                    c.execute("DELETE FROM event WHERE message_id =?", (messageID,))
                    conn.commit()
                else:
                    if str(userID) not in claimedID:
                        await self.createBal(None,userID)
                        c.execute(f"SELECT user_id, balance FROM econ WHERE user_id = ?",(userID,))
                        result2 = c.fetchone()
                        balance = int(result2[1])
                        memberBal = balance + cookies
                        val = (memberBal, userID)
                        c.execute("UPDATE econ SET balance = ? WHERE user_id = ?", val)
                        conn.commit()

                        if claimedID == '':
                            claimedID = userID
                        else:
                            claimedID =f'{claimedID} {userID}'
                        
                        c.execute("UPDATE event SET claimed_ids = ? WHERE message_id = ?", (claimedID,messageID))
                        conn.commit()
            conn.close()

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute(f"INSERT INTO invites(invite_id, uses,users) VALUES(?,?)",(invite.id,invite.uses))
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
    async def eventcookie(self,ctx,cookies,chosenDate=None,*args):
        dateErrorMSG = f'{ctx.message.author.mention} Invalid date specified. Input dates using the M/D/YYYY or M/D format. Dates must be of the future. Leave the date blank to make the event expire tomorrow'
        channel = self.client.get_channel(announcementsID)
        message = ' '.join(args)
        try:
            if not (cookies.isnumeric()):
                message = chosenDate
                chosenDate = cookies
                cookies = 1 
            if message is not None:
                dateList = list(chosenDate.split("/"))
                if len(dateList) == 2:
                    year = datetime.today().year
                    chosenDate = date(year,int(dateList[0]),int(dateList[1]))
                elif len(dateList) == 3:
                    chosenDate = date(int(dateList[2]),int(dateList[0]),int(dateList[1]))
                elif len(dateList) > 3 or len(dateList) == 1:
                    return await ctx.send(dateErrorMSG)
            else:
                message = chosenDate
                chosenDate = datetime.today() + timedelta(days=1)
            
            # Would be code to make sure that the user didn't supply a past date but I forgot how stupid this module is
            if datetime.now().date() > chosenDate:
                return await ctx.send(dateErrorMSG)

            def check(checkMessage):
                return checkMessage.author.id == ctx.message.author.id and checkMessage.channel.id == ctx.channel.id

            previewMessage = (
                f'Message: **{message}**\nValid Through: {chosenDate.strftime("%A %B %d %Y")}\nCookies upon reaction: {cookies}'
                f'\n{ctx.message.author.mention} Posting this to {channel.mention}. Reply ``c`` to cancel and any other key to proceed'
            )

            preview = await ctx.send(previewMessage)
            response = await self.client.wait_for('message', check=check, timeout=60.0)
            response = response.content

            if response == 'c':
                return await preview.edit(content='Post cancelled')
            
            bigboy = await channel.send(message)
            await bigboy.add_reaction('🍪')
            conn = sqlite3.connect('example.db')
            c = conn.cursor()
            timestamp = (chosenDate - date(1970, 1, 1)).total_seconds()
            val = (bigboy.id,cookies,timestamp,'')

            c.execute("INSERT INTO event(message_id,amount_cookies,end_date,claimed_ids) VALUES(?,?,?,?)", val)
            conn.commit()
            conn.close()

            await ctx.send(f'{ctx.message.author.mention} Event created. Check {channel.mention}')

        except ValueError:
           await ctx.send(dateErrorMSG)
        except asyncio.TimeoutError:
            await ctx.send(f'{ctx.message.author.mention} Response timed out')

    @commands.command()
    @commands.has_role(admin_role)
    async def givecookie(self,ctx, member: discord.Member, *args):
        # if member == ctx.message.author:
        #     return await ctx.send("You can't give yourself a cookie silly")
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        await self.createBal(ctx.channel, member.id)
        c.execute(f"SELECT user_id, balance FROM econ WHERE user_id = '{member.id}'")
        memberBal = int(c.fetchone()[1]) + rewards['modGift']
        val = (memberBal, member.id)
        c.execute("UPDATE econ SET balance = ? WHERE user_id = ?", val)
        conn.commit()
        reason = "None"
        if len(args) > 0:
            reason = " ".join(args)
        embed=embedsText(f'{ctx.message.author.display_name} gave {member.display_name} 5 :cookie:',f'Reason: {reason}')
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
                c.execute("SELECT * FROM users WHERE user_id=?", (member.id,))
                userInfo = c.fetchone()
                if userInfo is None:
                    c.execute("INSERT INTO users(user_id) VALUES(?)", (member.id,))
                    conn.commit()
                    if invite.uses > int(result[1]):
                        userID = invite.inviter.id
                        if not (invite.inviter.bot):
                            await self.createBal(None, userID)
                            c.execute(f"SELECT user_id, balance FROM econ WHERE user_id = '{userID}'")
                            result = c.fetchone()
                            memberBal = int(result[1]) + rewards['invite']
                            val = (memberBal, userID)
                            c.execute("UPDATE econ SET balance = ? WHERE user_id = ?", val)
                            conn.commit()
                            channel = await self.client.fetch_channel(int(config("GENERAL_ONE_CHANNEL_ID")))
                            await channel.send(f"<@{userID}> Thanks for inviting <@{member.id}> to the server. Have 3 :cookie:")
                        c.execute("UPDATE invites set uses = ? WHERE invite_id = ?", (invite.uses,invite.id))
                        conn.commit()
                        break

    # awards cookie when someone bumped disboard
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == int(config('DISBOARD_ID')):
            if self.check_all_message(":thumbsup:", message):
                m = re.search(r'<@!?(\d+)>', message.embeds[0].description)
                tag = m.group(0)
                member = tag
                member = member[2:-1]
                guild = self.client.get_guild(int(config('GUILD_ID')))
                member = guild.get_member(int(member))
                conn = sqlite3.connect('example.db')
                c = conn.cursor()
                await self.createBal(message.channel, member.id)
                c.execute(f"SELECT user_id, balance FROM econ WHERE user_id = '{member.id}'")
                memberBal = int(c.fetchone()[1]) + rewards['bump']
                val = (memberBal, member.id)
                c.execute("UPDATE econ SET balance = ? WHERE user_id = ?", val)
                conn.commit()
                channel = message.channel
                await channel.send(f"Thanks for bumping {member.display_name}, have a :cookie:!")
            '''
            # Don't use this code, it gives cookies for failed bumps
            elif self.check_all_message("until the server can be bumped", message):
                m = re.search(r'<@!?(\d+)>', message.embeds[0].description)
                tag = m.group(0)
                member = tag
                print("Bumped! Tag: " + member + " ID: " + member[2:-1])
                member = member[2:-1]
                guild = self.client.get_guild(int(config('GUILD_ID')))
                member = guild.get_member(int(member))
                conn = sqlite3.connect('example.db')
                c = conn.cursor()
                await self.createBal(message.channel, member.id)
                c.execute(f"SELECT user_id, balance FROM econ WHERE user_id = '{member.id}'")
                memberBal = int(c.fetchone()[1]) + rewards['bump']
                val = (memberBal, member.id)
                c.execute("UPDATE econ SET balance = ? WHERE user_id = ?", val)
                conn.commit()
                channel = message.channel
                await channel.send(f"Thanks for bumping {member.display_name}, have a :cookie:!")
            '''
    '''
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
    '''

    # allows user to check their own or another user's balance
    @commands.command(pass_context = True , aliases=['cookie', 'cookies', 'bal'])
    async def balance(self, ctx, member:discord.Member=None):
        memberID = ctx.author.id
        displayName = ctx.author.display_name
        name = ctx.author
        if member is not None:
            memberID = member.id
            displayName = member.display_name
            name = member
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        await self.createBal(ctx.channel, memberID)
        c.execute(f"SELECT user_id, balance FROM econ WHERE user_id = '{memberID}'")
        result = c.fetchone()
        bal = int(result[1])
        embed=embedsText(f'{displayName}\'s balance: {bal} :cookie:','')
        #currentDate = date.today()
        #today = currentDate.strftime('%m/%d/%Y').replace("/0", "/")
        #if today[0] == '0':
        #    today = today[1:]
        embed.set_footer(text=f"{name} • {config('PREFIX')}help cookies")
        await ctx.send(embed=embed)

    @commands.command(pass_context = True , aliases=['baltop'])
    async def leaderboard(self, ctx):
        guild = self.client.get_guild(int(config('GUILD_ID')))
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        i = 1
        rank = 1
        authorBalance = 0
        rank_found = False
        need_to_yeet = False
        users_to_yeet = []
        string = ''
        for row in c.execute("SELECT * FROM econ ORDER BY balance + 0 DESC"):
            balance = int(row[1])
            member = guild.get_member(int(row[0]))
            if member == None:
                need_to_yeet = True
                users_to_yeet.append(int(row[0]))
                continue
            if i <= 10:
                if balance > 0:
                    if i == 1:
                        string += f'\n:first_place:: **{balance}** :cookie: \t{member.display_name} ({str(member)})'
                    elif i == 2:
                        string += f'\n:second_place:: **{balance}** :cookie: \t{member.display_name} ({str(member)})'
                    elif i == 3:
                        string += f'\n:third_place:: **{balance}** :cookie: \t{member.display_name} ({str(member)})'
                    else:
                        string += f'\n#{i}: **{balance}** :cookie: \t{member.display_name} ({str(member)})'
                    i += 1
            if not rank_found:
                if member == ctx.message.author:
                    rank_found = True
                    authorBalance = balance
                    if i > 10:
                        break
                else:
                    rank += 1
            if rank_found and i > 10:
                break
            
        if need_to_yeet:
            for yeet in users_to_yeet:
                c.execute(f"DELETE FROM econ WHERE user_id = {yeet}")
            conn.commit()
            need_to_yeet = False

        embed=embedsText('TLC :cookie: Leaderboard', f'{string}')
        embed.set_footer(text=f"Your rank is #{rank} • You have {authorBalance} 🍪")
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

    async def createBal(self, channel, memberID):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute(f"SELECT user_id FROM econ WHERE user_id = ?", (memberID,))
        if c.fetchone() is None:
            val = (memberID, startingCookies)
            c.execute("INSERT INTO econ(user_id ,balance) VALUES(?,?)", val)
            if channel is not None:
                embed = embed=embedsText("It looks like you've never had cookies before",f"Use `{config('PREFIX')}help cookies` to learn more")
                await channel.send(embed=embed)
        conn.commit()
    
# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Cookies(client))

