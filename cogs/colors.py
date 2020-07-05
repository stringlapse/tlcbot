# yes I know this code is repetitive lemme sleep and use functions in the morning god

import discord
from discord.ext import commands
import urllib.request
from colorthief import ColorThief
from urllib.request import urlopen
from index import embedsText
import json
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM

class Colors(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    # Takes the dominant color of the image in a link and sends the color
    @commands.command()
    async def color(self, ctx, arg1, numColors=1:int):
        message = await ctx.send(f"{ctx.message.author.mention} detecting color... might take a few seconds")
        opener = urllib.request.URLopener()
        self.convertsIMGRecieved(arg1, opener)
        
        
        # gets photo of that color in svg
        jsonurl = urlopen("http://www.thecolorapi.com/id?rgb=rgb({0},{1},{2})".format(dominant_rgb[0],dominant_rgb[1],dominant_rgb[2]))
        text = json.loads(jsonurl.read())
        hexVal = text["hex"]["value"]
        name = text["name"]["value"]
        filename, headers = opener.retrieve(text["image"]["bare"], 'images/tempSVG.svg')

        # converts photo into usable format and sends
        f = self.convertsSVG()

        embed=embedsText(f' {name}','') 
        embed.set_image(url="attachment://imageSend.png")
        embed.set_footer(text=f' {hexVal}')
        await message.delete()
        await ctx.send(file=f, embed=embed)
    
    @commands.command()
    async def complement(self, ctx, arg1):
        message = await ctx.send(f"{ctx.message.author.mention} detecting color... might take a few seconds")
        opener = urllib.request.URLopener()
        self.convertsIMGRecieved(arg1, opener)
        dominant_rgb = self.grabsDominantColor()
        
        # gets photo of that color in svg
        jsonurl = urlopen("http://www.thecolorapi.com/scheme?rgb=rgb({0},{1},{2})&mode=complement&count=1".format(dominant_rgb[0],dominant_rgb[1],dominant_rgb[2]))
        text = json.loads(jsonurl.read())
        hexChosen = text["colors"][0]["hex"]["value"]
        hexChosen = hexChosen[1:]
        jsonurl = urlopen(f"http://www.thecolorapi.com/id?hex={hexChosen}")
        text = json.loads(jsonurl.read())
        name = text["name"]["value"]
        filename, headers = opener.retrieve(text["image"]["bare"], 'images/tempSVG.svg')

        # converts photo into usable format and sends
        f = self.convertsSVG()

        # embeds message and sends
        embed=embedsText(f' {name}','') 
        embed.set_image(url="attachment://imageSend.png")
        embed.set_footer(text=f' #{hexChosen}')
        await message.delete()
        await ctx.send(file=f, embed=embed)

    @commands.command()
    async def scheme(self, ctx, arg1):
        message = await ctx.send(f"{ctx.message.author.mention} detecting color... might take a few seconds")
        opener = urllib.request.URLopener()
        self.convertsIMGRecieved(arg1, opener)
        dominant_rgb = self.grabsDominantColor()
        
        # gets photo of that color in svg
        jsonurl = urlopen("http://www.thecolorapi.com/scheme?rgb=rgb({0},{1},{2})&count=5".format(dominant_rgb[0],dominant_rgb[1],dominant_rgb[2]))
        text = json.loads(jsonurl.read())
        colors = []
        hexes = []
        for i in range(0,5):
            name = text["colors"][i]["name"]["value"]
            hexVal = text["colors"][i]["name"]["closest_named_hex"]
            colors.append(name)
            hexes.append(hexVal)

        filename, headers = opener.retrieve(text["image"]["bare"], 'images/tempSVG.svg')

        # converts photo into usable format and sends
        f = self.convertsSVG()

        # embeds message and sends
        embed=embedsText(f' {", ".join(colors)}','') 
        embed.set_image(url="attachment://imageSend.png")
        embed.set_footer(text=f' {", ".join(hexes)}')
        await message.delete()
        await ctx.send(file=f, embed=embed)
    
        # takes photo url and saves it
    def convertsIMGRecieved(self,url, opener):
        opener.addheader('User-Agent', 'whatever')
        filename, headers = opener.retrieve(url, 'images/imageRecieved.jpg')

    # gets dominant (most widely used) color from image
    def grabsDominantColor(self):
        color_thief = ColorThief('images/imageRecieved.jpg')
        return color_thief.get_color(quality=1)

    # converts photo into usable format
    def convertsSVG(self):
        drawing = svg2rlg("images/tempSVG.svg")
        renderPM.drawToFile(drawing, "images/imageSend.png", fmt="PNG")
        return discord.File("images/imageSend.png",filename="imageSend.png")

# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Colors(client))

