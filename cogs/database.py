# testing out the functionality of a SQLite db
# for this example I created a table to host a basic economy

import discord
from discord.ext import commands
from index import admin_role
from decouple import config
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

        c.execute('''
        CREATE TABLE IF NOT EXISTS event(
        message_id text, 
        amount_cookies text, 
        end_date text, 
        claimed_ids text
            )
        ''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS channel(
        channel_id text,
        function text
            )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS invites(
        invite_id text,
        uses text
            )
        ''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS starboard(
        message_id text,
        bot_message_id text
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
        artstation text,
        twitch text,
        tiktok text,
        UNIQUE(user_id)
            )
        ''') 

        conn.commit()
        conn.close()
        print("database ready")
    
    @commands.command()
    @commands.has_role(admin_role)
    async def database(self,ctx):
        await ctx.send("The database has been DMed to you")
        await ctx.message.author.send(file=discord.File("example.db"))

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
    
