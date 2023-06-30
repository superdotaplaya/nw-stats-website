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
import testing_groups
import verification
import recruitment

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



@bot.slash_command(description = "Submits Screenshots for data processing.")
async def submitwarstats(ctx, server: Option(str, "What server did the war occur on?"), war_name: Option(str, "Name of the war.")):
    for role in ctx.author.roles:
        if str(role.id) == "1001600386450333747":
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

@bot.slash_command(description = "Submits Screenshots for data processing.")
async def submitinvasionstats(ctx, server: Option(str, "What server did the invasion occur on?"), invasion_name: Option(str, "Name of the invasion.")):
    for role in ctx.author.roles:
        if str(role.id) == "1027072479925129246":
            channel_to_read = bot.get_channel(ctx.channel.id)
            messages = await ctx.channel.history(limit=200).flatten()
            images = []
            for message in messages:
                print(message.content)
                for link in reversed(message.attachments):
                    images.append(link.url)
            print(images)
            await ctx.respond("Stats are being submitted, this may take a few minutes!")
            await ctx.send(analyze_screenshots.extract_text_invasion(images, invasion_name, server))

@bot.slash_command(guild_ids=[1001596849192444044], description = "Returns a given players monthly stat card")
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



@bot.slash_command(guild_ids=[1001596849192444044], description = "Once Screenshots are analyzed and stats are correct,this is used to add stats to the database")
async def enterwarstats(ctx, server: Option(str, "What server did the war occur on?"), war_id: Option(int,"What war Id are you adding to the database?")):
    for role in ctx.author.roles:
        if server.lower() == "val":
            server = "Valhalla"
        elif server.lower() == "cos":
            server = "Castle of Steel"
        elif server.lower() == "ygg":
            server = "Yggdrasil"
        elif server.lower() == "del":
            server = "Delos"
        elif server == "oro":
            server = "Orofena"
        elif server == "eri":
            server = "Eridu"
        elif server == "del":
            server = "Delos"
        if str(role.id) == "1001600386450333747":
            await ctx.respond("Attempting to add stats to the website, please wait a moment!")
            upload_stats = enter_stats.add_war(server,war_id)
            if upload_stats == f"Stats for this war are now live at: https://www.nw-stats.com/{server}/war/{war_id}":
                await ctx.send(upload_stats)
                await bot.get_channel(int(1017194084647047288)).send(f"Stats for this war are now live at: https://www.nw-stats.com/{server.replace(' ','%20')}/war/{war_id}")
            else:
                await ctx.send(upload_stats)


@bot.slash_command(guild_ids=[1001596849192444044], description = "Once Screenshots are analyzed and stats are correct,this is used to add stats to the database")
async def fixwarstats(ctx, server: Option(str, "What server did the war occur on?"), war_id: Option(str, "What war are you fixing the stats for?")):
    for role in ctx.author.roles:
        if str(role.id) == "1001600386450333747":
            await ctx.respond("Attempting to fix stats on the website, please wait a moment!")
            war_id = war_id
            server = server
            print(war_id)
            print(server)
            await ctx.send(enter_stats.fix_stats(server,war_id))



@bot.slash_command(guild_ids=[1001596849192444044], description = "Once Screenshots are analyzed and stats are correct,this is used to add stats to the database")
async def deleteinvasion(ctx, server: Option(str, "What server did the invasion occur on?"), invasion_id: Option(str, "What war are you deleting from the website?")):
    for role in ctx.author.roles:
        if str(role.id) == "1027072479925129246":
            await ctx.respond("Attempting to remove invasion from the site!")
            invasion_id = invasion_id
            server = server
            print(invasion_id)
            print(server)
            await ctx.send(enter_stats.remove_invasion(server,invasion_id))

@bot.slash_command(guild_ids=[1001596849192444044], description = "Once Screenshots are analyzed and stats are correct,this is used to add stats to the database")
async def enterinvasionstats(ctx, server: Option(str, "What server did the invasion occur on?"), invasion_id: Option(int,"What invasion Id are you adding to the database?")):
    for role in ctx.author.roles:
        if server.lower() == "val":
            server = "Valhalla"
        elif server.lower() == "cos":
            server = "Castle of Steel"
        elif server.lower() == "ygg":
            server = "Yggdrasil"
        elif server.lower() == "del":
            server = "Delos"
        elif server == "oro":
            server = "Orofena"
        elif server == "eri":
            server = "Eridu"
        elif server == "del":
            server = "Delos"
        if str(role.id) == "1027072479925129246":
            await ctx.respond("Attempting to add stats to the website, please wait a moment!")
            upload_stats = enter_stats.add_invasion(server,invasion_id)
            if upload_stats == f"Stats for this invasion are now live at: https://www.nw-stats.com/{server.replace(' ','%20')}/invasion/{invasion_id}":
                await ctx.send(upload_stats)
                await bot.get_channel(int(1027321184339107841)).send(f"Stats for this invasion are now live at: https://www.nw-stats.com/{server.replace(' ','%20')}/invasion/{invasion_id}")
            else:
                await ctx.send(upload_stats)


@bot.slash_command(guild_ids=[1001596849192444044], description = "Once Screenshots are analyzed and stats are correct,this is used to add stats to the database")
async def fixinvasionstats(ctx, server: Option(str, "What server did the invasion occur on?"), invasion_id: Option(str, "What invasion are you fixing the stats for?")):
    for role in ctx.author.roles:
        if str(role.id) == "1001600386450333747":
            await ctx.respond("Attempting to fix invasion stats on the website, please wait a moment!")
            invasion_id = invasion_id
            server = server
            print(invasion_id)
            print(server)
            await ctx.send(enter_stats.fix_invasion_stats(server,invasion_id))

@bot.slash_command(guild_ids=[1001596849192444044], description = "Once Screenshots are analyzed and stats are correct,this is used to delete a war from the site")
async def deletewar(ctx, server: Option(str, "What server did the war occur on?"), war_id: Option(str, "What war are you deleting from the website?")):
    for role in ctx.author.roles:
        if str(role.id) == "1001600386450333747":
            await ctx.respond("Attempting to remove invasion from the site!")
            war_id = war_id
            server = server
            print(war_id)
            print(server)
            await ctx.send(enter_stats.remove_war(server,war_id))

@bot.slash_command(guild_ids=[1001596849192444044], description = "Submit a war roster to be analyzed for the site.")
async def submitgroupstats(ctx, server: Option(str, "What server did the war occur on?"), war_id: Option(str, "What war are you submitting a roster for?"), attack_or_defense: Option(str, "Is this the attack or defense roster?")):
    images = []
    for role in ctx.author.roles:
        if str(role.id) == "1001600386450333747":
            channel_to_read = bot.get_channel(ctx.channel.id)
            messages = await ctx.channel.history(limit=200).flatten()
            for message in messages:
                print(message.content)
                for link in reversed(message.attachments):
                    images.append(link.url)
            image = images[0]
            await ctx.respond("Attempting to analyze war roster!")
            war_id = war_id
            server = server
            print(war_id)
            print(server)
            testing_groups.get_groups(image,war_id,server,attack_or_defense)
            await ctx.send("Roster Submitted!")


@bot.slash_command(guild_ids=[1001596849192444044], description = "Submit a war roster to be displayed on the site.")
async def entergroupstats(ctx, server: Option(str, "What server did the war occur on?"), war_id: Option(str, "What war are you entering a roster for?"), attack_or_defense: Option(str, "Is this the attack or defense roster?")):
    enter_stats.group_stats(server,war_id,attack_or_defense)
    await ctx.respond("Attempting to enter roster into the database!")
    await ctx.send("Roster submitted and should be viewable on the war scoreboard page!")

@bot.slash_command(guild_ids=[1001596849192444044], description = "Delete war roster for a war")
async def deletegroupstats(ctx, server: Option(str, "What server did the war occur on?"), war_id: Option(str, "What war are you deleting a roster for?"), attack_or_defense: Option(str, "Is this the attack or defense roster?")):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    sql = "DELETE FROM group_records WHERE server = %s AND war_id = %s AND group_team = %s"
    val = (server, war_id, attack_or_defense.title())
    mycursor.execute(sql, val)
    mydb.commit()
    await ctx.respond("Roster removed!")

@bot.slash_command(guild_ids=[1001596849192444044], description = "Delete war roster for a war")
async def fixgroupstats(ctx, server: Option(str, "What server did the war occur on?"), war_id: Option(str, "What war are you deleting a roster for?"), attack_or_defense: Option(str, "Is this the attack or defense roster?")):
    try:
        enter_stats.fixgroupstats(server,war_id,attack_or_defense)
        await ctx.respond("Roster removed!")
    except:
        await ctx.respond("An error occured")

@bot.slash_command(guild_ids=[1001596849192444044], description = "Delete war roster for a war")
async def verifyuser(ctx, user_id: Option(str, "What users Discord ID?"), verified_name: Option(str, "What is their verified name (from their submitted screenshot)?")):
    await ctx.respond(verification.verify_account(user_id,verified_name))

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


@bot.slash_command(guild_ids=[1001596849192444044], description = "Submit a recruitment message to the website!")
async def addrecruitment(ctx, server: Option(str, "What server are you recruiting on?"),company_name: Option(str, "What is the companies name?"), recruitment_message: Option(str, "What is the recruitment messsage?")):
    for role in ctx.author.roles:
        if str(role.id) == "1001600386450333747":
            await ctx.respond("Adding recruitment post to database!")
            recruitment.add_message(server,recruitment_message, company_name)
            await ctx.send(f"Recruitment message has been added on {server} for {company_name}!")

@bot.slash_command(guild_ids=[1001596849192444044], description = "Remove a recruitment message from the website!")
async def removerecruitment(ctx, server: Option(str, "What server are you removing the message from?"), company_name: Option(str, "What is the companies name?")):
    for role in ctx.author.roles:
        if str(role.id) == "1001600386450333747":
            await ctx.respond("Removing recruitment post from database!")
            recruitment.delete_message(server,company_name)
            await ctx.send("Recruitment message has been removed on {server}!")

bot.run(config.discord_token)
