# testing out the functionality of a SQLite db
# for this example I created a table to host a basic economy

import discord
from discord.ext import commands
import sqlite3
import re
from index import embedsText

class Database(commands.Cog):
    def __init__(self, client):
        self.client = client

    
    @commands.Cog.listener()
    async def on_ready(self):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()

        c.execute('''
        CREATE TABLE IF NOT EXISTS econ(
        user_id text,
        balance text
            )
        ''')
    
        print("Database created")


        c.execute('''
        CREATE TABLE IF NOT EXISTS shared_art(
        bot_message_id text,
        original_message_id text,
        image_url text,
        twitter text,
        instagram text
            )
        ''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS users(
        user_id text,
        twitter text,
        instagram text,
        youtube text,
        deviantart text,
        personal_website text,
        UNIQUE(user_id)
            )
        ''')   

        c.execute('''
        CREATE TABLE IF NOT EXISTS starboard(
        message_id text,
        bot_message_id text
            )
        ''')
        
        conn.commit()
        conn.close()
        print("database ready")
    
    
    # awards cookie when someone bumped disboard
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 728026870154526731:
            if self.check_all_message("Bump done :thumbsup:", message):
                m = re.search(r'<@!?(\d+)>', message.embeds[0].description)
                tag = m.group(0)
                member = tag
                removeChars = ["<",">","@"]
                for i in removeChars:
                    member = member.replace(i,"")
                conn = sqlite3.connect('example.db')
                c = conn.cursor()
                c.execute(f"SELECT user_id FROM econ WHERE user_id = '{member}'")
                if c.fetchone() is None:
                    val = (member, 5)
                    c.execute("INSERT INTO econ(user_id ,balance) VALUES(?,?)", val)
                    conn.commit()
                c.execute(f"SELECT user_id, balance FROM econ WHERE user_id = '{member}'")
                memberBal = int(c.fetchone()[1]) + 1
                val = (memberBal, member)
                c.execute("UPDATE econ SET balance = ? WHERE user_id = ?", val)
                conn.commit()
                embed=embedsText(f'Thanks for bumping. Have a :cookie:!','')
                channel = message.channel
                await channel.send(embed=embed)
         
    # simulates disboard's bump message
    @commands.command()
    async def bumpYes(self, ctx):
        embed = discord.Embed(title="DISBOARD: The Public Server List", 
                            url="https://disboard.org/",
                            description=f"{ctx.author.mention}\nBump done :thumbsup:\nCheck it on DISBOARD: https://disboard.org/")

        embed.set_image(url="https://disboard.org/images/bot-command-image-bump.png")
        await ctx.send(embed=embed)
    
    # simulates disboard's bump fail message
    @commands.command()
    async def bumpNo(self, ctx):
        embed = discord.Embed(title="DISBOARD: The Public Server List", 
                            url="https://disboard.org/",
                            description=f"{ctx.author.mention}, Please wait another 97 minutes until the server can be bumped")

        embed.set_thumbnail(url="https://disboard.org/images/bot-command-image-thumbnail-error.png")
        await ctx.send(embed=embed)

    # allows user to check their own or another user's balance
    @commands.command()
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
                string += f'\n#{i}: {user}\t{balance} :cookie:'
                i += 1
            if i > 10:
                break
        embed=embedsText('TLC Leaderboard', f'{string}')                                                              
        await ctx.send(embed=embed)
        
        
   
    def check_all_message(self,check_for, message):
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
        
# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Database(client))

        
# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Database(client))

# Adds a user to the database if they are not already there. Method does not work :( until message is deleted?
# def addsUser(guild_id, user_id):
#     conn = sqlite3.connect('example.db')
#     c = conn.cursor()
#     c.execute(f"SELECT user_id FROM econ WHERE guild_id = '{guild_id}' AND user_id = '{user_id}'")
#     noUser = c.fetchone() is None
#     if noUser:
#         val = (guild_id, user_id, 500)
#         c.execute("INSERT INTO econ(guild_id, user_id ,balance) VALUES(?,?,?)", val)
#         conn.commit()
    
