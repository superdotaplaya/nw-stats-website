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

@bot.slash_command(description = "Displays the number of Umbral Shards required to upgrade gear.")
async def shardcost(ctx, starting_gear_score: Option(str, "Enter The Gear score the item is starting at.", required = True), desired_gear_score: Option(str, "Enter the desired Gear score you would like to upgrade the item to.", required = True)):
    channel = str(ctx.channel)
    print(channel)
    if channel == "bot-commands":
        current_item_lvl = starting_gear_score
        desired_item_lvl = desired_gear_score
        get_shard_cost(current_item_lvl,desired_item_lvl)
        await ctx.respond(f"To upgrade your item from level {current_item_lvl} to {desired_item_lvl} you will need {get_shard_cost(current_item_lvl,desired_item_lvl)} umbral shard(s).")


@bot.slash_command(description = "Displays a table breaking down the Umbral shards earned from mutated dungeons.")
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

@bot.slash_command(description = "Displays Umbral Shard rewards based on expertise when opening Gypsum casts")
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




@bot.slash_command(description = "Displays stats about the given player on the given server!")
async def playerstats(ctx, server: Option(str, "What server is the player on? COS, YGG, VAL, DEL, ORO"), player_name: Option(str, "What is the players name?")):
    await ctx.respond("Attempting to find Stats, please wait a moment!")
    if server.lower() == 'val':
        server = 'Valhalla'
    elif server.lower() == 'oroa':
        server = 'Orofena'
    elif server.lower() == 'ygg':
        server = 'Yggdrasil'
    elif server.lower() == 'mar':
        server = 'Maramma'
    elif server.lower() == 'del':
        server = 'Delos'
    elif server.lower() == 'eri':
        server = 'Eridu'
    elif server.lower() == 'cos':
        server = 'Castle of Steel'
    data = calc_stats(player_name,server)
    embed = discord.Embed(
    title=f"{player_name}'s NW-Stats Profile ({server})", description="A breakdown of player stats gathered from war screenshots!", color=0x336EFF)
    embed.add_field(name="Average Kills", value=f"{data[1]}", inline=False)
    embed.add_field(name="Record Kills", value=f"{'{:,}'.format(int(data[8]))}", inline=False)
    embed.add_field(name="Average Damage", value=f"{'{:,}'.format(float(data[5]))}", inline=False)
    embed.add_field(name="Record Damage", value=f"{'{:,}'.format(int(data[10]))}", inline=False)
    embed.add_field(name="Average Healing", value=f"{'{:,}'.format(float(data[4]))}", inline=False)
    embed.add_field(name="Record Healing", value=f"{'{:,}'.format(float(data[9]))}", inline=False)
    embed.add_field(name="Average Assists", value=f"{'{:,}'.format(float(data[3]))}", inline=False)
    embed.add_field(name="Record Assists", value=f"{'{:,}'.format(float(data[25]))}", inline=False)
    embed.add_field(name="Profile Link", value=f"https://www.nw-stats.com/{server}/player/{player_name}", inline=False)
    embed.set_image(url="https://www.nw-stats.com/static/images/nw-stats%20logo.png")
    await ctx.send(embed=embed)


@bot.slash_command(description = "Displays the users last 5 wars on the given server.")
async def last5(ctx, server: Option(str, "What server is the player on?"), player_name: Option(str, "What is the players name?")):
    await ctx.respond("Attempting to find Stats, please wait a moment!")
    war_ids = []
    data = get_user_wars(player_name,"All", server)
    embed = discord.Embed(
    title=f"{player_name}'s Last 5 Wars", description="A quick look at the users 5 most recent wars on the requested server!", color=0x336EFF)
    embed.add_field(name="War Stats", value = "Breakdowns Below!", inline = False)
    bot.message_war_list = []
    for item in data:
        bot.message_war_list.append(str(item[9]))
        embed.add_field(name=f"War ID {item[9]}" , value = f"Score: {item[3]} | Kills: {item[4]} | Deaths: {item[5]} | Assists: {item[6]} | Healing: {item[7]} | damage: {item[8]}")
    embed.set_image(url="https://www.nw-stats.com/static/images/nw-stats%20logo.png")
    await ctx.send(embed=embed)


def calc_stats(usr,server):

    requested_player = usr
    print(f"sql_stuff {requested_player} {server}")
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )

    mycursor = mydb.cursor()
    # loop through the rows
    mycursor.execute("SELECT * FROM player_records")
    myresult = mycursor.fetchall()
    player_results = []
    player_score = []
    player_kills = []
    player_deaths = []
    player_assists = []
    player_healing = []
    player_damage = []
    war_names = []
    player_kpars = []
    wins = []
    losses = []
    roles_played = []
    wars_played_in = []
    for row in myresult:
        # Get the players won and lost wars for win/loss stats

        if row[2].lower() == requested_player.lower() and row[16].lower() == server.lower():
            roles_played.append(row[15].lower())
            if "*" not in row[3]:
                player_results.append(row)
                wars_played_in.append(row[9])
            if row[13] == row[14] and row[14] != "N/A":
                wins.append(row)
            elif row[13] != row[14] and row[14] != "N/A":
                losses.append(row)
    if len(player_results) != 0:
        player_results.sort(key = lambda x: int(x[4].replace("*","").replace("^","")), reverse = True)
        max_kill_war = player_results[0][9]
        player_results.sort(key = lambda x: int(x[7].replace("*","").replace("^","")), reverse = True)
        max_healing_war = player_results[0][9]
        player_results.sort(key = lambda x: int(x[8].replace("*","").replace("^","")), reverse = True)
        max_damage_war = player_results[0][9]
        player_results.sort(key = lambda x: int(x[6].replace("*","").replace("^","")), reverse = True)
        max_assists_war = player_results[0][9]
        for player_entry in player_results:

            if "*" not in player_entry[3]:
                print(player_entry)
                score = player_entry[3]
                kills = player_entry[4]
                deaths = player_entry[5]
                assists = player_entry[6]
                healing = player_entry[7]
                damage = player_entry[8]
                player_score.append(int(score))
                player_kills.append(int(kills))
                player_deaths.append(int(deaths))
                player_assists.append(int(assists))
                player_healing.append(int(healing))
                player_damage.append(int(damage))
                if player_entry[11] != "N/A":
                    player_kpars.append(float(player_entry[11]))

        avg_score = sum(player_score)/len(player_score)
        avg_kills = sum(player_kills)/len(player_kills)
        avg_deaths = sum(player_deaths)/len(player_deaths)
        avg_assists = sum(player_assists)/len(player_assists)
        avg_healing = sum(player_healing)/len(player_healing)
        avg_damage = sum(player_damage)/len(player_damage)
        if sum(player_deaths) != 0:
            healing_per_death = sum(player_healing)/sum(player_deaths)
            damage_per_death = sum(player_damage)/sum(player_deaths)
            assists_per_death = sum(player_assists)/sum(player_deaths)
            kills_per_death = sum(player_kills)/sum(player_deaths)
            kills_plus_assists_per_death = (sum(player_kills)+sum(player_assists))/sum(player_deaths)
        else:
            healing_per_death = sum(player_healing)/1
            damage_per_death = sum(player_damage)/1
            assists_per_death = sum(player_assists)/1
            kills_per_death = sum(player_kills)/1
            kills_plus_assists_per_death = (sum(player_kills)+sum(player_assists))/1
        max_kills = max(player_kills)
        max_healing = max(player_healing)
        max_damage = max(player_damage)
        max_assists = max(player_assists)
        total_healing = sum(player_healing)
        total_assists = sum(player_assists)
        total_damage = sum(player_damage)
        total_deaths = sum(player_deaths)
        total_kills = sum(player_kills)
        total_wins = len(wins)
        total_losses = len(losses)
        average_kpar = sum(player_kpars)/len(player_kpars)


        def get_healing_graph(player_healing, wars_played_in):
            return(0)



        def get_damage_graph(player_damage, wars_played_in):
            return(0)


        player_stats = ["{:.2f}".format(avg_score),"{:.2f}".format(avg_kills),"{:.2f}".format(avg_deaths),"{:.2f}".format(avg_assists),"{:.2f}".format(avg_healing),"{:.2f}".format(avg_damage), "{:.2f}".format(healing_per_death), "{:.2f}".format(damage_per_death), max_kills, max_healing, max_damage, "{:.2f}".format(assists_per_death), total_kills, total_deaths, total_assists, total_damage, total_healing, "{:.2f}".format(kills_plus_assists_per_death),"{:.2f}".format(kills_per_death),get_healing_graph(player_healing, wars_played_in),get_damage_graph(player_damage, wars_played_in),max_healing_war,max_kill_war,max_assists_war,max_damage_war, max_assists, total_wins, total_losses, "{:.2f}".format(average_kpar), roles_played]

        return(player_stats)
    else:
        return([0,0,0,0,0,0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0, 0, 0, 0, 0, []])

@bot.slash_command(description = "Gives a link to download the NW-Stats companion app.")
async def companion(ctx):
    await ctx.respond("Download and learn more about the NW-Stats companion app here: https://www.nw-stats.com/companion")


def get_user_wars(usr,role,server):
    requested_player = usr
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # loop through the rows
    sql = "SELECT * FROM player_records WHERE name = %s AND server = %s"
    val =(requested_player,server.lower())
    mycursor.execute(sql,val)
    player_results = mycursor.fetchall()
    attacks = []
    defenses = []
    misc = []
    player_results.sort(key = lambda x: int(x[9].replace("*","").replace("^","")), reverse = True)
    return(player_results[:5])
bot.run(config.discord_token_users)


#run the bot
 #Get your bot token from https://discordapp.com/developers/applications/

