from audioop import avg
import os, sys, discord, platform, random, aiohttp, json
from datetime import datetime
import time
import json
import discord
from discord.ext import commands
from discord.commands import Option
import pygsheets
import requests
import threading
import asyncio
from langdetect import detect
from bs4 import BeautifulSoup
import analyze_screenshots
import lxml
import mysql.connector
import enter_stats


#from PIL import Image
bot = discord.Bot()


gc = pygsheets.authorize(service_file='credentials.json')
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config





def get_current_requests(sheet_id):
    id = sheet_id
    sh = gc.open('New World Crafting Ques')
    wks = sh.worksheet_by_title("Tuna")
    returned_values = wks.get_values_batch( ['A2:A250'] )
    returned_list = []
    for item in returned_values[0][:]:
        if item != []:
            returned_list.append(item)
    print(returned_list)
    return(returned_list)

def get_request_id(sheet_id):
    id = sheet_id
    sh = gc.open('New World Crafting Ques')
    wks = sh.worksheet_by_title("Tuna")
    current_highest_id = wks.get_value("J6")
    return(current_highest_id)

def increase_request_id(sheet_id):
    id = sheet_id
    sh = gc.open('New World Crafting Ques')
    wks = sh.worksheet_by_title("Tuna")
    current_highest_id = int(wks.get_value("J6"))
    current_highest_id += 1
    updating_cell = wks.cell("J6")
    updating_cell.set_value(current_highest_id)

def get_all_stats(player_name):
    sh = gc.open('Black Tuna Squad War Stats')
    wks = sh.worksheet_by_title("Running Average Stats")
    returned_values = wks.get_values_batch( ['A3:U500'] )
    for item in returned_values[0]:
        if item[0].lower() == player_name.lower():
            avg_kills = item[16]
            avg_healing = item[19]
            avg_KDA = item[18]
            avg_assists = item[17]
            avg_damage = item[20]
            max_kills = item[7]
            max_healing = item[13]
            max_KDA = item[11]
            max_assists = item[9]
            max_damage = item[15]
            wars_tracked = item[5]
            return(wars_tracked,avg_kills,avg_healing,avg_KDA,avg_assists,avg_damage,max_kills,max_healing,max_KDA,max_assists,max_damage)

def get_monthly_stats(player_name):
    sh = gc.open('Black Tuna Squad War Stats')
    mydate = datetime.now()
    full_month_name = mydate.strftime("%B")
    print(full_month_name)
    sheet_name = f"{str(full_month_name)} Averages"
    wks = sh.worksheet_by_title(str(sheet_name))
    returned_values = wks.get_values_batch( ['A3:U500'] )
    for item in returned_values[0]:
        if item[0].lower() == player_name.lower():
            avg_kills = item[16]
            avg_healing = item[19]
            avg_KDA = item[18]
            avg_assists = item[17]
            avg_damage = item[20]
            max_kills = item[7]
            max_healing = item[13]
            max_KDA = item[11]
            max_assists = item[9]
            max_damage = item[15]
            wars_tracked = item[5]
            return(full_month_name,wars_tracked,avg_kills,avg_healing,avg_KDA,avg_assists,avg_damage,max_kills,max_healing,max_KDA,max_assists,max_damage)

def get_player_name(player_name):
    sh = gc.open('Black Tuna Squad War Stats')
    wks = sh.worksheet_by_title("Marauder Member class / weapons")
    returned_values = wks.get_values_batch( ['A2:B500'] )
    for item in returned_values[0]:
        if item[0].lower() == player_name.lower():
            return(item[0])

def get_player_role(player_name):
    sh = gc.open('Black Tuna Squad War Stats')
    wks = sh.worksheet_by_title("Marauder Member class / weapons")
    returned_values = wks.get_values_batch( ['A2:B500'] )
    for item in returned_values[0]:
        if item[0].lower() == player_name.lower():
            return(item[1])

def get_avg_kda(player_name):
    sh = gc.open('Black Tuna Squad War Stats')
    wks = sh.worksheet_by_title("Running Average Stats")
    returned_values = wks.get_values_batch( ['A3:P500'] )
    for item in returned_values[0]:
        if item[0].lower() == player_name.lower():
            return(item[18])

def get_record_kda(player_name):
    sh = gc.open('Black Tuna Squad War Stats')
    wks = sh.worksheet_by_title("Running Average Stats")
    returned_values = wks.get_values_batch( ['A3:P500'] )
    for item in returned_values[0]:
        if item[0].lower() == player_name.lower():
            return(item[2])

def get_avg_healing(player_name):
    sh = gc.open('Black Tuna Squad War Stats')
    wks = sh.worksheet_by_title("Running Average Stats")
    returned_values = wks.get_values_batch( ['A3:P500'] )
    for item in returned_values[0]:
        if item[0].lower() == player_name.lower():
            return(item[14])

def get_record_healing(player_name):
    sh = gc.open('Black Tuna Squad War Stats')
    wks = sh.worksheet_by_title("Running Average Stats")
    returned_values = wks.get_values_batch( ['A3:P500'] )
    for item in returned_values[0]:
        if item[0].lower() == player_name.lower():
            return(item[2])

def get_avg_damage(player_name):
    sh = gc.open('Black Tuna Squad War Stats')
    wks = sh.worksheet_by_title("Running Average Stats")
    returned_values = wks.get_values_batch( ['A3:P500'] )
    for item in returned_values[0]:
        if item[0].lower() == player_name.lower():
            return(item[15])

def get_record_damage(player_name):
    sh = gc.open('Black Tuna Squad War Stats')
    wks = sh.worksheet_by_title("Running Average Stats")
    returned_values = wks.get_values_batch( ['A3:P500'] )
    for item in returned_values[0]:
        if item[0].lower() == player_name.lower():
            return(item[2])

def get_player_role(player_name):
    sh = gc.open('Black Tuna Squad War Stats')
    wks = sh.worksheet_by_title("Marauder Member class / weapons")
    returned_values = wks.get_values_batch( ['A2:P500'] )
    for item in returned_values[0]:
        if item[0].lower() == player_name.lower():
            return(item[1])

def get_player_kills(player_name):
    sh = gc.open('Black Tuna Squad War Stats')
    wks = sh.worksheet_by_title("Running Average Stats")
    returned_values = wks.get_values_batch( ['A3:P500'] )
    for item in returned_values[0]:
        if item[0].lower() == player_name.lower():
            return(item[11])

def get_record_kills(player_name):
    sh = gc.open('Black Tuna Squad War Stats')
    wks = sh.worksheet_by_title("Running Average Stats")
    returned_values = wks.get_values_batch( ['A3:P500'] )
    for item in returned_values[0]:
        if item[0].lower() == player_name.lower():
            return(item[15])

def get_avg_assists(player_name):
    sh = gc.open('Black Tuna Squad War Stats')
    wks = sh.worksheet_by_title("Running Average Stats")
    returned_values = wks.get_values_batch( ['A3:P500'] )
    for item in returned_values[0]:
        if item[0].lower() == player_name.lower():
            return(item[12])

def get_record_assists(player_name):
    sh = gc.open('Black Tuna Squad War Stats')
    wks = sh.worksheet_by_title("Running Average Stats")
    returned_values = wks.get_values_batch( ['A3:P500'] )
    for item in returned_values[0]:
        if item[0].lower() == player_name.lower():
            return(item[2])

def check_for_sheet(ctx):
    id = ctx
    list_of_sheets = []
    new_list = []
    found = False
    sh = gc.open('New World Crafting Ques')
    wks = sh[0]
    try:
        sh.worksheets(sheet_property='title', value=str(id), force_fetch=False)
        return(True)
    except pygsheets.WorksheetNotFound:
        return(False)

def get_current_requests(sheet_id):
    id = sheet_id
    sh = gc.open('New World Crafting Ques')
    wks = sh.worksheet_by_title(str(id))
    returned_values = wks.get_values_batch( ['A2:A250'] )
    returned_list = []
    for item in returned_values[0][:]:
        if item != []:
            returned_list.append(item)
    print(returned_list)
    return(returned_list)

def get_request_id(sheet_id):
    id = sheet_id
    sh = gc.open('New World Crafting Ques')
    wks = sh.worksheet_by_title(str(id))
    current_highest_id = wks.get_value("J6")
    return(current_highest_id)

def increase_request_id(sheet_id):
    id = sheet_id
    sh = gc.open('New World Crafting Ques')
    wks = sh.worksheet_by_title(str(id))
    current_highest_id = int(wks.get_value("J6"))
    current_highest_id += 1
    updating_cell = wks.cell("J6")
    updating_cell.set_value(current_highest_id)

def get_shard_cost(current_lvl, desired_lvl):
    current_level = int(current_lvl)
    desired_level = int(desired_lvl)
    total_shards = 0
    cost_chart = [[590,0],[591,2],[592,4],[593,6],[594,10],[595,20],[596,35],[597,50],[598,65],[599,90],[600,125],[601,1],[602,2],[603,3],[604,4],[605,5],[606,6],[607,8],[608,10],[609,15],[610,20],[611,25],[612,35],[613,50],[614,65],[615,90],[616,125],[617,175],[618,250],[619,325],[620,450],[621,900],[622,1000],[623,1400],[624,1900],[625,2500]]
    print(current_level)
    print(desired_level)
    for item in cost_chart:
        if item[0] == int(current_level):
            item_start_point = cost_chart.index(item)
        if item[0] == int(desired_level):
            item_end_point = cost_chart.index(item)
    print(cost_chart[item_start_point+1:item_end_point+1])
    for item in cost_chart[item_start_point+1:item_end_point+1]:
        total_shards += int(item[1])
    print(total_shards)
    return(total_shards)
    #for item in cost_chart[item_start_point+1:item_end_point]:
     #   total_shards += int(item[1])
    #print(total_shards)

"""def combine_images(images):
    images_list = ["img_1.png","img_2.png","img_3.png","img_4.png","img_5.png","img_6.png","img_7.png","img_8.png",]
    new_images_list= []
    try:
        os.remove("leaderboard.png")
    except:
        pass
    for image_to_delete in images_list:
        try:
            os.remove(image_to_delete)
        except:
            pass

    for image in images:
        response = requests.get(str(image))
        file = open(f"img_{images.index(image) + 1}.png", "wb")
        print(response)
        file.write(response.content)
        file.close()
        new_images_list.append(f"img_{images.index(image) + 1}.png")
    print(new_images_list)

    imgs = [Image.open(i) for i in new_images_list]

    # If you're using an older version of Pillow, you might have to use .size[0] instead of .width
    # and later on, .size[1] instead of .height
    min_img_width = min(i.width for i in imgs)

    total_height = 0
    for i, img in enumerate(imgs):
        # If the image is larger than the minimum width, resize it
        if img.width > min_img_width:
            imgs[i] = img.resize((min_img_width, int(img.height / img.width * min_img_width)), Image.ANTIALIAS)
        total_height += imgs[i].height

    # I have picked the mode of the first image to be generic. You may have other ideas
    # Now that we know the total height of all of the resized images, we know the height of our final image
    img_merge = Image.new(imgs[0].mode, (min_img_width, total_height))
    y = 0
    for img in imgs:
        img_merge.paste(img, (0, y))

        y += img.height
    img_merge.save('leaderboard.png')
    leaderboard = "leaderboard.png"
    return(leaderboard)"""

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    #first_run = False
    #await asyncio.create_task(check_forums(10, stuff))

@bot.slash_command(guild_ids=[892232759513350174], description = "Displays the number of Umbral Shards required to upgrade gear.")
async def shardcost(ctx, starting_gear_score: Option(str, "Enter The Gear score the item is starting at.", required = True), desired_gear_score: Option(str, "Enter the desired Gear score you would like to upgrade the item to.", required = True)):
    channel = str(ctx.channel)
    print(channel)
    if channel == "bot-commands":
        current_item_lvl = starting_gear_score
        desired_item_lvl = desired_gear_score
        get_shard_cost(current_item_lvl,desired_item_lvl)
        await ctx.respond(f"To upgrade your item from level {current_item_lvl} to {desired_item_lvl} you will need {get_shard_cost(current_item_lvl,desired_item_lvl)} umbral shard(s).")

@bot.slash_command(guild_ids=[892232759513350174], description = "Submit an item you are looking to be crafted.,")
async def submitcraftrequest(ctx, item_name: Option(str,"Enter the name of the item (not the perks)",required = True),perk_1: Option(str,"Enter the first perk you are looking for", required = True), perk_2: Option(str,"Enter the second perk you are looking for", required = True), perk_3: Option(str,"Enter the third perk you are looking for", required = True)):
    channel = str(ctx.channel)
    print(ctx.interaction.user.id)
    if channel == "crafting-help":
        sh = gc.open('New World Crafting Ques')
        member = ctx.author
        wks = sh.worksheet_by_title("Tuna")
        username = str(ctx.interaction.user)
        returned_list = get_current_requests("Tuna")
        embed=discord.Embed(title=f"{username}'s craft request", description=f"{username} has submitted a crafting request! React with ❌ to cancel or mark the request as finished! View the request below!", color=0xFF5733)
        embed.add_field(name="Item Name", value=item_name, inline=True)
        embed.add_field(name="First Perk", value=perk_1, inline=False)
        embed.add_field(name="Second Perk", value=perk_2, inline=False)
        embed.add_field(name="Third Perk", value=perk_3, inline=False)
        status_msg = await ctx.respond("Submitting request, please wait a moment!")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("❌")
        returned_list.append([str(msg.id)])
        i = 0
        while i <= 100:
            returned_list.append([''])
            i += 1
        print(returned_list)
        pygsheets.datarange.DataRange(start="A2", end=f"A{len(returned_list)+1}", worksheet=wks).update_values(values=returned_list[:])
        increase_request_id("Tuna")
    else:
        await ctx.respond("This command can only be used in the #crafting-help channel!")


@bot.slash_command(guild_ids=[892232759513350174], description = "Displays a table breaking down the Umbral shards earned from mutated dungeons.")
async def shardbreakdown(ctx):
        channel = str(ctx.channel)
        print(channel)
        if channel == "bot-commands":
            embed = discord.Embed(title="Umbral Shard Reward Breakdown", description="This is the breakdown of how many Umbral Shards can be earned per dungeon and completion rating.", color=0x0e01f9)
            embed.add_field(name="----------------------------------", value="Difficulty 1", inline=False)
            embed.add_field(name="Bronze", value="27 shards", inline=True)
            embed.add_field(name="Silver", value="33 shards", inline=True)
            embed.add_field(name="Gold", value="40 shards", inline=True)
            embed.add_field(name="----------------------------------", value="Difficulty 2", inline=False)
            embed.add_field(name="Bronze", value="40 shards", inline=True)
            embed.add_field(name="Silver", value="50 shards", inline=True)
            embed.add_field(name="Gold", value="60 shards", inline=True)
            embed.add_field(name="----------------------------------", value="Difficulty 3", inline=False)
            embed.add_field(name="Bronze", value="53 shards", inline=True)
            embed.add_field(name="Silver", value="67 shards", inline=True)
            embed.add_field(name="Gold", value="80 shards", inline=True)
            embed.add_field(name="----------------------------------", value="Difficulty 4", inline=False)
            embed.add_field(name="Bronze", value="80 shards", inline=True)
            embed.add_field(name="Silver", value="100 shards", inline=True)
            embed.add_field(name="Gold", value="120 shards", inline=True)
            embed.add_field(name="----------------------------------", value="Difficulty 5", inline=False)
            embed.add_field(name="Bronze", value="133 shards", inline=True)
            embed.add_field(name="Silver", value="167 shards", inline=True)
            embed.add_field(name="Gold", value="200 shards", inline=True)
            embed1 = discord.Embed(title="Umbral Shard Reward Breakdown", description="This is the breakdown of how many Umbral Shards can be earned per dungeon and completion rating.", color=0x0e01f9)
            embed1.add_field(name="----------------------------------", value="Difficulty 6", inline=False)
            embed1.add_field(name="Bronze", value="533 shards", inline=True)
            embed1.add_field(name="Silver", value="667 shards", inline=True)
            embed1.add_field(name="Gold", value="800 shards", inline=True)

            embed1.add_field(name="----------------------------------", value="Difficulty 7", inline=False)
            embed1.add_field(name="Bronze", value="1000 shards", inline=True)
            embed1.add_field(name="Silver", value="1250 shards", inline=True)
            embed1.add_field(name="Gold", value="1500 shards", inline=True)

            embed1.add_field(name="----------------------------------", value="Difficulty 8", inline=False)
            embed1.add_field(name="Bronze", value="1333 shards", inline=True)
            embed1.add_field(name="Silver", value="1667 shards", inline=True)
            embed1.add_field(name="Gold", value="2000 shards", inline=True)
            embed1.add_field(name="----------------------------------", value="Difficulty 9", inline=False)
            embed1.add_field(name="Bronze", value="2667 shards", inline=True)
            embed1.add_field(name="Silver", value="3333 shards", inline=True)
            embed1.add_field(name="Gold", value="4000 shards", inline=True)
            embed1.add_field(name="----------------------------------", value="Difficulty 10", inline=False)
            embed1.add_field(name="Bronze", value="4000 shards", inline=True)
            embed1.add_field(name="Silver", value="5000 shards", inline=True)
            embed1.add_field(name="Gold", value="6000 shards", inline=True)
            await ctx.respond(embed=embed)
            await ctx.respond(embed=embed1)

@bot.slash_command(guild_ids=[892232759513350174], description = "Displays Umbral Shard rewards based on expertise when opening Gypsum casts")
async def gypsumshards(ctx):
        channel = str(ctx.channel)
        print(channel)
        if channel == "bot-commands":
            await ctx.respond("""```                    Expertise Level | Shards Reward
                            600             | 100
                            601             | 112
                            602             | 124
                            603             | 136
                            604             | 148
                            605             | 160
                            606             | 172
                            607             | 184
                            608             | 196
                            609             | 208
                            610             | 220
                            611             | 232
                            612             | 244
                            613             | 256
                            614             | 268
                            615             | 280
                            616             | 292
                            617             | 304
                            618             | 316
                            619             | 328
                            620             | 340
                            621             | 352
                            622             | 364
                            623             | 376
                            624             | 388
                            625             | 400```""")


#Check a players role for PVP
@bot.slash_command(guild_ids=[892232759513350174], description = "Returns a given players role in PVP")
async def checkrole(ctx,player_name: Option(str, "Enter the name of the player whos role you are checking.", required = True)):
    channel = str(ctx.channel)
    print(channel)
    if channel == "bot-commands":
        sh = gc.open('Black Tuna Squad War Stats')
        wks = sh.worksheet_by_title("Marauder Member class / weapons")
        returned_values = wks.get_values_batch( ['A2:D500'] )
        for item in returned_values[0]:
            if item[0].lower() == player_name:
                await ctx.respond(f"{item[0]} plays as a {item[1]}")

@bot.slash_command(guild_ids=[892232759513350174], description = "Combines leaderboard images to create one long list for easier browsing.")
async def combinescores(ctx,img_1: Option(str, "Enter the first image", required = True),img_2: Option(str, "Enter the second image", required = True),img_3: Option(str, "Enter the third image", required = False),img_4: Option(str, "Enter the fourth image", required = False),img_5: Option(str, "Enter the fifth image", required = False),img_6: Option(str, "Enter the 6th image", required = False),img_7: Option(str, "Enter the 7th image", required = False),img_8: Option(str, "Enter the last image", required = False)):
    channel = str(ctx.channel)
    print(channel)
    if channel == "bot-commands":
        image_list = []
        if img_1:
            image_list.append(img_1)
        if img_2:
            image_list.append(img_2)
        if img_3:
            image_list.append(img_3)
        if img_4:
            image_list.append(img_4)
        if img_5:
            image_list.append(img_5)
        if img_6:
            image_list.append(img_6)
        if img_7:
            image_list.append(img_7)
        if img_8:
            image_list.append(img_8)
        print(image_list)
        combine_images(image_list)
        await ctx.send(file=discord.File('leaderboard.png'))
#Check a players average KDA
@bot.slash_command(guild_ids=[892232759513350174], description = "Returns a given players average KDA")
async def checkkda(ctx,player_name: Option(str, "Enter the name of the player whos KDA you are checking.", required = True)):
    channel = str(ctx.channel)
    print(channel)
    if channel == "bot-commands":
        sh = gc.open('Black Tuna Squad War Stats')
        wks = sh.worksheet_by_title("Average KDA's")
        returned_values = wks.get_values_batch( ['A2:B500'] )
        for item in returned_values[0]:
            if item[0].lower() == player_name.lower():
                await ctx.respond(f"{item[0]} has an average KDA of {item[1]} in recorded wars")

#check a players average damage
@bot.slash_command(guild_ids=[892232759513350174], description = "Returns a given players average KDA")
async def checkdamage(ctx,player_name: Option(str, "Enter the name of the player whos damage you are checking.", required = True)):
    channel = str(ctx.channel)
    print(channel)
    if channel == "bot-commands":
        sh = gc.open('Black Tuna Squad War Stats')
        wks = sh.worksheet_by_title("Average Damage")
        returned_values = wks.get_values_batch( ['A2:B500'] )
        for item in returned_values[0]:
            if item[0].lower() == player_name.lower():
                await ctx.respond(f"{item[0]} has an average damage of {item[1]} in recorded wars")

#check a players average healing
@bot.slash_command(guild_ids=[892232759513350174], description = "Returns a given players average KDA")
async def checkhealing(ctx,player_name: Option(str, "Enter the name of the player whos healing you are checking.", required = True)):
    channel = str(ctx.channel)
    print(channel)
    if channel == "bot-commands":
        sh = gc.open('Black Tuna Squad War Stats')
        wks = sh.worksheet_by_title("Average Healing")
        returned_values = wks.get_values_batch( ['A2:B500'] )
        for item in returned_values[0]:
            if item[0].lower() == player_name.lower():
                await ctx.respond(f"{item[0]} has an average healing of {item[1]} in recorded wars")

#check a players average kills
@bot.slash_command(guild_ids=[892232759513350174], description = "Returns a given players average KDA")
async def checkkills(ctx,player_name: Option(str, "Enter the name of the player whos kills you are checking.", required = True)):
    channel = str(ctx.channel)
    print(channel)
    if channel == "bot-commands":
        sh = gc.open('Black Tuna Squad War Stats')
        wks = sh.worksheet_by_title("Average Kills")
        returned_values = wks.get_values_batch( ['A2:B500'] )
        for item in returned_values[0]:
            if item[0].lower() == player_name.lower():
                await ctx.respond(f"{item[0]} has an average of {item[1]} kill(s) in recorded wars")

#check a players highest kills record
@bot.slash_command(guild_ids=[892232759513350174], description = "Returns a given players highest kills in all wars")
async def checkrecordkills(ctx,player_name: Option(str, "Enter the name of the player whos kills you are checking.", required = True)):
    channel = str(ctx.channel)
    print(channel)
    if channel == "bot-commands":
        sh = gc.open('Black Tuna Squad War Stats')
        wks = sh.worksheet_by_title("Average Kills")
        returned_values = wks.get_values_batch( ['A2:C500'] )
        for item in returned_values[0]:
            if item[0].lower() == player_name.lower():
                await ctx.respond(f"{item[0]} has a record of {item[2]} kill(s) in recorded wars")

@bot.slash_command(guild_ids=[892232759513350174], description = "Returns a given players highest healing in all wars")
async def checkrecordhealing(ctx,player_name: Option(str, "Enter the name of the player whos healing you are checking.", required = True)):
    channel = str(ctx.channel)
    print(channel)
    if channel == "bot-commands":
        sh = gc.open('Black Tuna Squad War Stats')
        wks = sh.worksheet_by_title("Average Healing")
        returned_values = wks.get_values_batch( ['A2:C500'] )
        for item in returned_values[0]:
            if item[0].lower() == player_name.lower():
                await ctx.respond(f"{item[0]} has a record of {item[2]} healing in recorded wars")

@bot.slash_command(guild_ids=[892232759513350174], description = "Returns a given players highest healing in all wars")
async def checkrecordkda(ctx,player_name: Option(str, "Enter the name of the player whos KDA you are checking.", required = True)):
    channel = str(ctx.channel)
    print(channel)
    if channel == "bot-commands":
        sh = gc.open('Black Tuna Squad War Stats')
        wks = sh.worksheet_by_title("Average KDA's")
        returned_values = wks.get_values_batch( ['A2:C500'] )
        for item in returned_values[0]:
            if item[0].lower() == player_name.lower():
                await ctx.respond(f"{item[0]} has a record KDA of {item[2]} in recorded wars")

@bot.slash_command(guild_ids=[892232759513350174], description = "Returns a given players highest healing in all wars")
async def checkrecorddamage(ctx,player_name: Option(str, "Enter the name of the player whos KDA you are checking.", required = True)):
    channel = str(ctx.channel)
    print(channel)
    if channel == "bot-commands":
        sh = gc.open('Black Tuna Squad War Stats')
        wks = sh.worksheet_by_title("Average Damage")
        returned_values = wks.get_values_batch( ['A2:C500'] )
        for item in returned_values[0]:
            if item[0].lower() == player_name.lower():
                await ctx.respond(f"{item[0]} has a record damage of {item[2]} in recorded wars")

@bot.slash_command(guild_ids=[892232759513350174], description = "Returns a given players stat card")
async def checkstats(ctx,player_name: Option(str, "Enter the name of the player whos stat card you would like to view.", required = True)):
    channel = str(ctx.channel)
    print(channel)
    if channel == "bot-commands":
        msg = await ctx.respond("Checking stats, They will be available below in a moment!")
        player_name_entered = get_player_name(player_name)
        wars_tracked,avg_kills,avg_healing,avg_KDA,avg_assists,avg_damage,max_kills,max_healing,max_KDA,max_assists,max_damage = get_all_stats(player_name_entered)
        embed = discord.Embed(
        title=f"{player_name_entered}'s Recorded Stats", description="A breakdown of player stats gathered from war screenshots.", color=0x336EFF)
        embed.add_field(name="Player Role", value=f"{get_player_role(player_name)}", inline=True)
        embed.add_field(name="Wars Tracked", value=f"{wars_tracked}", inline=True)
        embed.add_field(name="Average Kills", value=f"{avg_kills}", inline=False)
        embed.add_field(name="Record Kills", value=f"{max_kills}", inline=False)
        embed.add_field(name="Average Damage", value=f"{avg_damage}", inline=False)
        embed.add_field(name="Record Damage", value=f"{max_damage}", inline=False)
        embed.add_field(name="Average Healing", value=f"{avg_healing}", inline=False)
        embed.add_field(name="Record Healing", value=f"{max_healing}", inline=False)
        embed.add_field(name="Average KDA", value=f"{avg_KDA}", inline=False)
        embed.add_field(name="Record KDA", value=f"{max_KDA}", inline=False)
        embed.add_field(name="Average Assists", value=f"{avg_assists}", inline=False)
        embed.add_field(name="Record Assists", value=f"{max_assists}", inline=False)
        await ctx.send(embed=embed)

@bot.slash_command(guild_ids=[892232759513350174], description = "Returns a given players monthly stat card")
async def monthlystats(ctx,player_name: Option(str, "Enter the name of the player whos stat card you would like to view.", required = True)):
    channel = str(ctx.channel)
    print(channel)
    if channel == "bot-commands":
        msg = await ctx.respond("Checking stats, They will be available below in a moment!")
        player_name_entered = get_player_name(player_name)
        full_month_name,wars_tracked,avg_kills,avg_healing,avg_KDA,avg_assists,avg_damage,max_kills,max_healing,max_KDA,max_assists,max_damage = get_monthly_stats(player_name_entered)
        embed = discord.Embed(
        title=f"{player_name_entered}'s Recorded Stats For {full_month_name}", description="A breakdown of player stats gathered from war screenshots in the current month", color=0x336EFF)
        embed.add_field(name="Player Role", value=f"{get_player_role(player_name)}", inline=True)
        embed.add_field(name="Wars Tracked", value=f"{wars_tracked}", inline=True)
        embed.add_field(name="Average Kills", value=f"{avg_kills}", inline=False)
        embed.add_field(name="Record Kills", value=f"{max_kills}", inline=False)
        embed.add_field(name="Average Damage", value=f"{avg_damage}", inline=False)
        embed.add_field(name="Record Damage", value=f"{max_damage}", inline=False)
        embed.add_field(name="Average Healing", value=f"{avg_healing}", inline=False)
        embed.add_field(name="Record Healing", value=f"{max_healing}", inline=False)
        embed.add_field(name="Average KDA", value=f"{avg_KDA}", inline=False)
        embed.add_field(name="Record KDA", value=f"{max_KDA}", inline=False)
        embed.add_field(name="Average Assists", value=f"{avg_assists}", inline=False)
        embed.add_field(name="Record Assists", value=f"{max_assists}", inline=False)
        await ctx.send(embed=embed)

@bot.event
async def on_raw_reaction_add(payload):
    sh = gc.open('New World Crafting Ques')
    wks = sh.worksheet_by_title("Tuna")
    returned_values = wks.get_values_batch( ['A2:A100'] )
    message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    print(payload.emoji.name)
    if payload.user_id != 918401607585107969 and payload.emoji.name == "❌":
        for item in returned_values[0]:
            if str(item[0]) == str(message.id):
                await message.delete()

"""async def stuff():
    await asyncio.sleep(random.random() * 3)


async def check_forums(timeout, stuff):
    await asyncio.sleep(timeout)
    await stuff()
    last_forum_posts_id = []
    task = asyncio.create_task(check_forums(60, stuff))
    x = requests.get('https://newworldfans.com/api/v1/dev_tracker?page=1&source=forum')
    data = x.json()
    last_forum_posts = data[0:20]



    with open('last_msg.txt', 'r+') as f:

        recorded_posts = f.readlines()
        for item in last_forum_posts:
            if str(item['id']) not in recorded_posts and str(item['id'])+'\n' not in recorded_posts and str(detect(str(item['title']))) == "en" and str(detect(str(item['content']))) == "en":
                embed = discord.Embed(
                title=f"{item['title']}", description="New post on the forums by a developer!",url = item['source_url'], color=0x336EFF)
                embed.set_author(name=f"{item['developer_name']}")
                text_content = BeautifulSoup(item['content'][0:1000], "lxml").text
                embed.add_field(name="Content", value=f"{text_content}", inline=True)
                await bot.get_channel(951259667001143346).send("<@&953761787591942224> New developer post!")
                await bot.get_channel(951259667001143346).send(embed=embed)

            last_forum_posts_id.append(str(item['id']))
        f.seek(0)
        f.writelines('\n'.join(last_forum_posts_id))
        f.truncate()"""

@bot.slash_command(description = "Submits Screenshots for data processing.")
async def submitwarstats(ctx, server: Option(str, "What server did the war occur on?"), war_name: Option(str, "Name of the war.")):
    channel_to_read = bot.get_channel(ctx.channel.id)
    messages = await ctx.channel.history(limit=200).flatten()
    images = []
    for message in messages:
        print(message.content)
        for link in reversed(message.attachments):
            images.append(link.url)
    print(images)
    await ctx.respond("Stats are being submitted, this may take a few minutes!")
    await ctx.send(analyze_screenshots.extract_text(images, war_name, server))

@bot.slash_command(guild_ids=[892232759513350174], description = "Returns a given players monthly stat card")
async def submit_stats(ctx):
    mydb = mysql.connector.connect(
    host="superdotaplaya.mysql.pythonanywhere-services.com",
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )

    mycursor = mydb.cursor()
    sh = gc.open('Testing war dumps')
    info = sh.worksheets()
    last_sheet = info[-1].title
    wks = sh.worksheet_by_title(str(last_sheet)+1)
    returned_values = wks.get_values_batch( ['A1:H500'] )
    for player in returned_values[0]:
        player_name = player[1]
        player_score = player[2]
        player_kills = player[3]
        player_deaths = player[4]
        player_assists = player[5]
        player_healing = player[6]
        player_damage = player[7]
        data = (player_name,player_score,player_kills,player_deaths,player_assists,player_healing,player_damage)
        insert_stmt = (
    "INSERT INTO player_records(name, score, kills, deaths, assists, healing, damage)"
    "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
        print(data)
        mycursor.execute(insert_stmt, data)
        mydb.commit()

@bot.slash_command(description = "Returns a given players monthly stat card", )
async def warregister(ctx, player_name: Option(str, "Enter your in game name.", required = True),player_role: Option(str, "Enter the role you are looking to play (be specific!)", required = True), player_gear_score: Option(str, "Enter your gear score for this role.", required = True)):
    sh = gc.open('Tuna War Registration')
    wks = sh.worksheet_by_title("Sheet1")
    returned_values = wks.get_values_batch( ['A1:C200'] )
    print(returned_values)
    returned_values[0].append([player_name,player_role,player_gear_score])
    pygsheets.datarange.DataRange(start="A1", end="C1000", worksheet=wks).update_values(values=returned_values[0])
    await ctx.respond("Your registration information has been registered!")

@bot.slash_command(description = "Once Screenshots are analyzed and stats are correct,this is used to add stats to the database")
async def enterwarstats(ctx, server: Option(str, "What server did the war occur on?"), war_id: Option(int,"What war Id are you adding to the database?")):
    try:
        print(f"{server} + {war_id}")
        enter_stats.add_war(server,war_id)
        await ctx.respond("War has been added to the database, check the website to ensure everything is correct!")
    except:
        await ctx.send("Could not fully enter stats, plase try again later after checking to make sure the spreadsheet is correctly filled out!")

@bot.slash_command(description = "Once Screenshots are analyzed and stats are correct,this is used to add stats to the database")
async def fixwarstats(ctx, server: Option(str, "What server did the war occur on?"), war_id: Option(str, "What war are you fixing the stats for?")):
    try:
        war_id = war_id
        server = server
        print(war_id)
        print(server)
        enter_stats.fix_stats(server,war_id)
        await ctx.respond(f"Stats for https://www.nw-stats.com/{server}/war/{war_id} have been updated to reflect the information in the spreadsheet!")
    except:
        await ctx.respond("Could not enter war, try again later, or ensure all information is filled in correctly in the spreadsheet!")
bot.run(config.discord_token)


#run the bot
 #Get your bot token from https://discordapp.com/developers/applications/

