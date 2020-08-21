# yes I know this code is repetitive lemme sleep and use functions in the morning god

import discord
from discord.ext import commands
import urllib.request
from colorthief import ColorThief
from urllib.request import urlopen
from index import embedsText
import json
from svglib.svglib import svg2rlg
import random

from reportlab.graphics import renderPDF, renderPM

class Colors(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    # Takes the dominant color of the image in a link and sends the color
    @commands.command()
    async def colorphoto(self, ctx, num, mode='normal', link=None):
        if not num.isnumeric():
            mode = num
            num = 3
        if num > 6:
            return await ctx.send(f"{ctx.message.author.mention} woah slow down there. I can only show between three to six colors")
        if num < 3:
            return await ctx.send(f"{ctx.message.author.mention} too little colors. Please pick a number between three and six.")
        message = await ctx.send(f"{ctx.message.author.mention} detecting color... might take a few seconds")
        opener = urllib.request.URLopener()
        if link is None:
            attachments = ctx.message.attachments
            if len(attachments) == 0:
                return await message.edit(content=f"{ctx.message.author.mention} please supply some sort of media: link or attached photo")
            link = attachments[0].url

        self.convertsIMGRecieved(link, opener)

        # gets photo of the colors in svg
        palette = self.grabsPalette(num)
        colors = []
        hexes = []
        svgText = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="200">'
        increment = 200/(num)
        curY = 0
        
        for rgb in palette:
            hexVal = None
            name = None
            if mode == 'normal':
                jsonurl = urlopen("http://www.thecolorapi.com/id?rgb=rgb({0},{1},{2})".format(rgb[0],rgb[1],rgb[2]))
                text = json.loads(jsonurl.read())
                hexVal = text["hex"]["value"]
                name = text["name"]["value"]
            elif mode == 'compliment':
                jsonurl = urlopen("http://www.thecolorapi.com/scheme?rgb=rgb({0},{1},{2})&mode=complement&count=1)".format(rgb[0],rgb[1],rgb[2]))
                text = json.loads(jsonurl.read())
                hexVal = text["colors"][0]["hex"]["value"]
                hexChosen = hexVal[1:]
                jsonurl = urlopen(f"http://www.thecolorapi.com/id?hex={hexChosen}")
                text = json.loads(jsonurl.read())
                name = text["name"]["value"]
            if hexVal is None or name is None:
                await ctx.send(f"{ctx.message.author.mention} invalid mode specified")
            hexes.append(f'{hexVal}') 
            colors.append(name)
            svgText = svgText + "<rect fill=\"" + str(hexVal) + "\" x=\"0\" y=\"" + str(curY) + "\" width=\"100\" height=\"" + str(increment) + "\"></rect>"
            curY = curY + increment
        tempSVG = open('images/tempSVG.svg','w')
        tempSVG.write(svgText + "</svg>")
        tempSVG.close()
        f = self.convertsSVG()
        embed=embedsText(f' {", ".join(colors)}','')
        embed.set_image(url="attachment://imageSend.png")
        embed.set_footer(text=f' {", ".join(hexes)}')
        await message.delete()
        await ctx.send(file=f, embed=embed)

    @commands.command()
    async def color(self, ctx, color='random'):
        try:
            url = None
            if color[0] == "#" and len(color) == 6:
                color = color[1:]
                url = f'http://www.thecolorapi.com/id?hex={color}'
            elif '(' in color and ')' in color:
                url = f'http://www.thecolorapi.com/id?rgb={color}'
            elif color == 'random':
                R = random.randrange(1,250)
                G = random.randrange(1,250)
                B = random.randrange(1,250)
                url = f'http://www.thecolorapi.com/id?rgb=({R},{G},{B})'
            else:
                return await ctx.send(f"{ctx.message.author.mention} only accepts RGB or hex. Make sure your RGB value is surrounded by paranthesis with no spaces in between \"(A,B,C)\" and your hex value begins with a #")
            jsonurl = urlopen(url)
            text = json.loads(jsonurl.read())
            name = text["name"]["value"]
            hexVal = text["hex"]["value"]

            opener = urllib.request.URLopener()
            filename, headers = opener.retrieve(text["image"]["bare"], 'images/tempSVG.svg')

            # converts photo into usable format and sends
            f = self.convertsSVG()

            # embeds message and sends
            embed=embedsText(f'{name}','') 
            embed.set_image(url="attachment://imageSend.png")
            embed.set_footer(text=f' {hexVal}')
            await ctx.send(file=f, embed=embed)
        except urllib.error.HTTPError:
            return await ctx.send(f"{ctx.message.author.mention} only accepts RGB or hex. Make sure your RGB value is surrounded by paranthesis with no spaces in between \"(A,B,C)\" and your hex value begins with a #")


            

    @commands.command()
    async def scheme(self, ctx, color = 'random'):
        try:
            url = 'http://www.thecolorapi.com/scheme'
            if color[0] == "#" and len(color) == 6:
                color = color[1:]
                url = url + f'?hex={color}'
            elif '(' in color and ')' in color:
                url = url + f'?rgb={color}'
            elif color == 'random':
                R = random.randrange(1,250)
                G = random.randrange(1,250)
                B = random.randrange(1,250)
                url = f'http://www.thecolorapi.com/scheme?rgb=({R},{G},{B})'
            else:
                return await ctx.send(f"{ctx.message.author.mention} only accepts RGB or hex. Make sure your RGB value is surrounded by paranthesis with no spaces in between \"(A,B,C)\" and your hex value begins with a #")
            
            
            # gets photo of that color in svg
            mode = ['triad','complement','monochrome','quad']
            url = url + f'&mode={mode[random.randrange(0,len(mode))]}&count=4'
            print(url)
            jsonurl = urlopen(url)
            text = json.loads(jsonurl.read())
            colors = []
            hexes = []
            for i in range(0,4):
                name = text["colors"][i]["name"]["value"]
                hexVal = text["colors"][i]["name"]["closest_named_hex"]
                colors.append(name)
                hexes.append(hexVal)

            opener = urllib.request.URLopener()
            filename, headers = opener.retrieve(text["image"]["bare"], 'images/tempSVG.svg')

            # converts photo into usable format and sends
            f = self.convertsSVG()

            # embeds message and sends
            embed=embedsText(f' {", ".join(colors)}','') 
            embed.set_image(url="attachment://imageSend.png")
            embed.set_footer(text=f' {", ".join(hexes)}')
            await ctx.send(file=f, embed=embed)
        except urllib.error.HTTPError:
            return await ctx.send(f"{ctx.message.author.mention} only accepts RGB or hex. Make sure your RGB value is surrounded by paranthesis with no spaces in between \"(A,B,C)\" and your hex value begins with a #")
    
        # takes photo url and saves it
    def convertsIMGRecieved(self,url, opener):
        opener.addheader('User-Agent', 'whatever')
        filename, headers = opener.retrieve(url, 'images/imageRecieved.jpg')

    # gets dominant (most widely used) color from image
    def grabsDominantColor(self):
        color_thief = ColorThief('images/imageRecieved.jpg')
        return color_thief.get_color(quality=1)
    
    def grabsPalette(self, num):
        num = num-1
        color_thief = ColorThief('images/imageRecieved.jpg')
        return color_thief.get_palette(color_count=num)

    # converts photo into usable format
    def convertsSVG(self):
        drawing = svg2rlg("images/tempSVG.svg")
        renderPM.drawToFile(drawing, "images/imageSend.png", fmt="PNG")
        return discord.File("images/imageSend.png",filename="imageSend.png")

# Required for the cog to be read by the bot
def setup(client):
    client.add_cog(Colors(client))

