# testing out the functionality of a SQLite db
# for this example I created a table to host a basic economy

import discord
from discord.ext import commands
import sqlite3
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
        guild_id text,
        user_id text,
        balance text
            )
        ''')

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
        commission_sheet text,
        UNIQUE(user_id)
            )
        ''')    
        
        conn.commit()
        conn.close()
        print("database ready")
    
    @commands.command()
    async def balance(self, ctx):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute(f"SELECT user_id FROM econ WHERE guild_id = '{ctx.author.guild.id}' AND user_id = '{ctx.author.id}'")
        noUser = c.fetchone() is None
        if noUser:
            val = (ctx.author.guild.id, ctx.author.id, 5)
            c.execute("INSERT INTO econ(guild_id, user_id ,balance) VALUES(?,?,?)", val)
            conn.commit()
        c.execute(f"SELECT user_id, balance FROM econ WHERE guild_id = '{ctx.author.guild.id}' AND user_id = '{ctx.author.id}'")
        result = c.fetchone()
        bal = int(result[1])
        embed=embedsText(f'{ctx.message.author}\'s balance', f'{bal} :cookie:!')
        await ctx.send(embed=embed)
    
    @commands.command()
    async def pay(self,ctx, member: discord.Member, amount: int):
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute(f"SELECT user_id FROM econ WHERE guild_id = '{ctx.author.guild.id}' AND user_id = '{ctx.author.id}'")
        if c.fetchone() is None:
            val = (ctx.author.guild.id, ctx.author.id, 5)
            c.execute("INSERT INTO econ(guild_id, user_id ,balance) VALUES(?,?,?)", val)
            conn.commit()
        # this check should honestly be put into its own function but when I tried that the code took too long to execute
        c.execute(f"SELECT user_id FROM econ WHERE guild_id = '{member.guild.id}' AND user_id = '{member.id}'")
        if c.fetchone() is None:
            val = (member.guild.id, member.guild.id, 5)
            c.execute("INSERT INTO econ(guild_id, user_id ,balance) VALUES(?,?,?)", val)
            conn.commit()
        c.execute(f"SELECT user_id, balance FROM econ WHERE guild_id = '{ctx.author.guild.id}' AND user_id = '{ctx.author.id}'")
        result = c.fetchone()
        balAfterTransaction = int(result[1]) - amount
        if balAfterTransaction < 0:
            await ctx.send("Insufficent funds")
        else:
            c.execute(f"SELECT user_id, balance FROM econ WHERE guild_id = '{member.guild.id}' AND user_id = '{member.id}'")
            memberBal = int(c.fetchone()[1]) + amount
            val = (memberBal, member.guild.id, member.id)
            c.execute("UPDATE econ SET balance = ? WHERE guild_id = ? and user_id = ?", val)
            conn.commit()
            val = (balAfterTransaction, ctx.author.guild.id, ctx.author.id)
            c.execute("UPDATE econ SET balance = ? WHERE guild_id = ? and user_id = ?", val)
            conn.commit()
            embed=embedsText(f'Sent {amount} :cookie: to {member}','')
            await ctx.send(embed=embed)
        
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
    
