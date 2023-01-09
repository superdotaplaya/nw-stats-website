from flask import Flask, redirect, url_for, render_template, request, session
import pygsheets
import sql_stuff
import mysql.connector
import getpass
import os
from requests_oauthlib import OAuth2Session
import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import mpld3
import config
from mpld3 import plugins
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import sys
import time
import requests
from bs4 import BeautifulSoup
import re
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from mysql.connector import Error


# Disable SSL requirement
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Settings for your app
base_discord_api_url = 'https://discordapp.com/api'
client_id = config.client_id
client_secret = config.client_secret
redirect_uri=config.redirect_uri
scope = config.scope
token_url = config.token_url
authorize_url = config.authorize_url

admin_list = config.admin_list

app = Flask(__name__)
app.secret_key = config.app_key
app.permanent_session_lifetime = datetime.timedelta(days=14)
app.config["SESSION_PERMANENT"] = True
app.config['UPLOAD_FOLDER'] = "mysite/assets/images/player_gear/"
app.config['MAX_CONTENT_PATH'] = 200000
region_names = ["US WEST","US EAST","SA EAST","EU CENTRAL","AP SOUTHEAST"]
territory_list = ['Cutlass Keys', 'First Light', 'Monarchs Bluffs', 'Windsward','Reekwater','Ebonscale Reach','Everfall', 'Restless Shore', 'Weavers Fen', 'Brightwood', 'Mourningdale', 'Brimstone Sands']
gc = pygsheets.authorize(service_file='credentials.json')
import config

def is_logged_in():
    try:
        if session['logged_in'] == True:
            return(True)
    except:
        return(False)

def has_ads():
    try:
        if session['no-ads'] == True:
            return(False)
        else:
            return(True)
    except:
        return(True)

def get_damage_graph(attacker_damage, defender_damage):

    x = "attacker"
    y = attacker_damage
    x1 = "defender"
    y1 = defender_damage
    fig, ax = plt.subplots()
    ax.grid(True, alpha=0.3)


    boxes = ax.bar(x,y)
    boxes1 = ax.bar(x1,y1)

    ax.set_title('Attack Vs. Defense Damage', size=20)
    ax.set_xticks([])
    ax.set_xticks([], minor=True)
    plt.legend(loc='upper right')
    plt.gca().legend(('Attackers','Defenders'))
    plt.figure(figsize = (10, 5))
    for i, box in enumerate(boxes.get_children()):
        tooltip = mpld3.plugins.LineLabelTooltip(box, label=f"Attack {attacker_damage}")
        mpld3.plugins.connect(fig, tooltip)
    plugins.connect(fig, tooltip)
    for i, box in enumerate(boxes1.get_children()):
        tooltip = mpld3.plugins.LineLabelTooltip(box, label=f"Defense: {defender_damage}")
        mpld3.plugins.connect(fig, tooltip)
    plugins.connect(fig, tooltip)

    return(mpld3.fig_to_html(fig))

def update_all_servers():

    data_indexes = ["'0'","'1'","'2'","'3'","'4'"]
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # loop through the rows
    sql = "SELECT * FROM server_list"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    print(myresult)
    x = requests.get('https://www.newworld.com/en-us/support/server-status')

    soup = BeautifulSoup(x.content, 'html.parser')

    server_num = 0
    for region in region_names:
        servers_to_add = []
        data_index = data_indexes[server_num]
        divs = soup.select(f"[data-index={data_index}]")
        found = False
        for div in divs:
            server_name = div.text.replace("\n","").lstrip().rstrip()
            server_name = re.sub(r'([^\s])\s([^\s])', r'\1_\2',server_name)
            server_names = server_name.split(" ")
            server_names = list(filter(lambda x: x != '', server_names))
            if server_names[0].replace("_", " ") not in region_names:
                servers_to_add.append(server_names)
        if len(servers_to_add) != 0:
            print(servers_to_add[1])
            sql = "UPDATE server_list SET server_names = %s WHERE region_name = %s"
            val = (','.join(servers_to_add[1]),region)
            mycursor.execute(sql, val)
            mydb.commit()
        server_num += 1

def get_all_servers(region):
    if region != "ALL":
        mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
        )
        mycursor = mydb.cursor()
        # loop through the rows
        sql = f"SELECT * FROM server_list WHERE region_name = {region}"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        servers = myresult[0][1].split(",")
        return(servers)
    return([])

def get_all_servers_global():
    all_servers = []
    servers = []
    mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
        )
    mycursor = mydb.cursor()
    # loop through the rows
    sql = "SELECT * FROM server_list"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for item in myresult:
        servers = item[1].split(",")
        print(item)
        for server in servers:
            print(server)
            all_servers.append(server.replace("_"," "))
    all_servers_sorted = sorted(all_servers)
    return(all_servers_sorted)

def get_leaderboards(category,server):
    mynewresult = []
    players = []
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # loop through the rows
    sql = "SELECT * FROM player_averages WHERE server = %s"
    val = (server,)
    mycursor.execute(sql,val)
    myresult = mycursor.fetchall()
    if category == 'score':
        myresult.sort(key = lambda x: float(x[2].replace("*","").replace("^","")), reverse = True)
    if category == 'kills':
        myresult.sort(key = lambda x: float(x[3].replace("*","").replace("^","")), reverse = True)
    if category == 'assists':
        myresult.sort(key = lambda x: float(x[4].replace("*","").replace("^","")), reverse = True)
    if category == 'healing':
        myresult.sort(key = lambda x: float(x[5].replace("*","").replace("^","")), reverse = True)
    if category =='damage':
        myresult.sort(key = lambda x: float(x[6].replace("*","").replace("^","")), reverse = True)
    for item in myresult:
        if int(item[7]) >= 10 and item[0].lstrip().rstrip().lower() not in players:
           players.append(item[0].lower())
           mynewresult.append(item)

    return(mynewresult[:10])

def get_healing_graph(attacker_healing, defender_healing):


    x = ["attacker"]
    y = attacker_healing
    x1 = ["defender"]
    y1 = defender_healing
    fig, ax = plt.subplots()
    ax.grid(True, alpha=0.3)

    boxes = ax.bar(x,y)
    boxes1 = ax.bar(x1,y1)

    ax.set_title('Attack Vs. Defense Healing', size=20)
    ax.set_xticks([])
    ax.set_xticks([], minor=True)
    plt.legend(loc='upper right')
    plt.gca().legend(('Attackers','Defenders'))



    for i, box in enumerate(boxes.get_children()):
        tooltip = mpld3.plugins.LineLabelTooltip(box, label=f"Attack: {attacker_healing}")
        mpld3.plugins.connect(fig, tooltip)
    plugins.connect(fig, tooltip)
    for i, box in enumerate(boxes1.get_children()):
        tooltip = mpld3.plugins.LineLabelTooltip(box, label=f"Defense: {defender_healing}")
        mpld3.plugins.connect(fig, tooltip)
    plugins.connect(fig, tooltip)

    return(mpld3.fig_to_html(fig))


def get_player_gear(player):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # loop through the rows
    sql = "SELECT * FROM player_gear WHERE player_name = %s"
    val = (player,)
    mycursor.execute(sql,val)
    myresult = mycursor.fetchall()
    print(myresult)
    if myresult == []:
        return([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])
    else:
        return(myresult)


def get_war_stats(war_id,sort_by,server):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # loop through the rows
    sql = "SELECT * FROM player_records WHERE war_id = %s AND server = %s"
    val = (war_id,server)
    mycursor.execute(sql,val)
    myresult = mycursor.fetchall()
    war_stats = []
    attacker_damage = []
    attacker_healing = []
    defender_damage = []
    defender_healing = []
    attacker_kills = []
    attacker_deaths = []
    attacker_assists = []

    defender_kills = []
    defender_deaths = []
    defender_assists = []
    war_winner = ""
    has_teams = False
    for row in myresult:
        war_stats.append(row)
        if row[13] == "Attack":
            attacker_damage.append(int(row[8].replace("*","").replace("^","")))
            attacker_kills.append(int(row[4].replace("*","").replace("^","")))
            attacker_deaths.append(int(row[5].replace("*","").replace("^","")))
            attacker_assists.append(int(row[6].replace("*","").replace("^","")))
            has_teams = True
        elif row[13] == "Defense":
            defender_damage.append(int(row[8].replace("*","").replace("^","")))
            defender_kills.append(int(row[4].replace("*","").replace("^","")))
            defender_deaths.append(int(row[5].replace("*","").replace("^","")))
            defender_assists.append(int(row[6].replace("*","").replace("^","")))
            has_teams = True
        if row[13] == "Attack":
            attacker_healing.append(int(row[7].replace("*","").replace("^","")))
            has_teams = True
        elif row[13] == "Defense":
            defender_healing.append(int(row[7].replace("*","").replace("^","")))
            has_teams = True
    if has_teams == True:
        total_attacker_damage = sum(attacker_damage)
        total_defender_damage = sum(defender_damage)
        total_attacker_healing = sum(attacker_healing)
        total_defender_healing = sum(defender_healing)
        total_attacker_kills = sum(attacker_kills)
        total_defender_kills = sum(defender_kills)
        total_attacker_deaths = sum(attacker_deaths)
        total_defender_deaths = sum(defender_deaths)
        total_attacker_assists = sum(attacker_assists)
        total_defender_assists = sum(defender_assists)
        attacker_dmg_per_kill = round((sum(attacker_damage)/sum(defender_deaths)),2)
        defender_dmg_per_kill = round((sum(defender_damage)/sum(attacker_deaths)),2)
        war_winner = row[14]
        if str(sort_by) == 'kills':
            war_stats.sort(key = lambda x: int(x[4].replace("*","").replace("^","")), reverse = True)

            return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
        if str(sort_by) == 'deaths':
            war_stats.sort(key = lambda x: int(x[5].replace("*","").replace("^","")), reverse = True)

            return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
        if str(sort_by) == 'assists':
            war_stats.sort(key = lambda x: int(x[6].replace("*","").replace("^","")), reverse = True)

            return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
        if str(sort_by) == 'healing':
            war_stats.sort(key = lambda x: int(x[7].replace("*","").replace("^","")), reverse = True)

            return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
        if str(sort_by) == 'damage':
            war_stats.sort(key = lambda x: int(x[8].replace("*","").replace("^","")), reverse = True)

            return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
        if str(sort_by) == 'kpar':
            try:
                war_stats.sort(key = lambda x: float(x[11].replace("*","").replace("^","").replace(",","")), reverse = True)
                return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
            except ValueError:
                return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
        if str(sort_by) == 'dmgkpar':
            try:
                war_stats.sort(key = lambda x: int(float(x[12].replace("*","").replace("^","").replace(",",""))), reverse = True)
                return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
            except ValueError:
                return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
        if str(sort_by) == 'team':
            war_stats.sort(key = lambda x: x[13], reverse = True)

            return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
        if sort_by == "none":
            return([war_stats],0,0, war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
        if str(sort_by) == 'role':
            try:
                war_stats.sort(key = lambda x: x[15], reverse = False)
                return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
            except ValueError:
                return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
        if sort_by == "none":
            return([war_stats], "","")
    else:
        if str(sort_by) == 'kills':
            war_stats.sort(key = lambda x: int(x[4].replace("*","").replace("^","")), reverse = True)

            return([war_stats], "","")
        if str(sort_by) == 'deaths':
            war_stats.sort(key = lambda x: int(x[5].replace("*","").replace("^","")), reverse = True)

            return([war_stats], "","")
        if str(sort_by) == 'assists':
            war_stats.sort(key = lambda x: int(x[6].replace("*","").replace("^","")), reverse = True)

            return([war_stats], "","")
        if str(sort_by) == 'healing':
            war_stats.sort(key = lambda x: int(x[7].replace("*","").replace("^","")), reverse = True)

            return([war_stats], "","")
        if str(sort_by) == 'damage':
            war_stats.sort(key = lambda x: int(x[8].replace("*","").replace("^","")), reverse = True)

            return([war_stats], "","")
        if str(sort_by) == 'kpar':
            try:
                war_stats.sort(key = lambda x: int(float(x[11].replace("*","").replace("^","").replace(",",""))), reverse = True)
                return([war_stats], "","")
            except ValueError:
                return([war_stats], "","")
        if str(sort_by) == 'dmgkpar':
            try:
                war_stats.sort(key = lambda x: int(float(x[12].replace("*","").replace("^","").replace(",",""))), reverse = True)
                return([war_stats], "","")
            except ValueError:
                return([war_stats], "","")
        if str(sort_by) == 'role':
            try:
                war_stats.sort(key = lambda x: x[15], reverse = True)
                return([war_stats], "","")
            except ValueError:
                return([war_stats], "","")
        if sort_by == "none":
            return([war_stats], "","")

def get_invasion_stats(invasion_id,sort_by,server):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # loop through the rows
    sql = "SELECT * FROM invasion_records WHERE invasion_id = %s AND server = %s"
    val = (invasion_id,server)
    mycursor.execute(sql,val)
    myresult = mycursor.fetchall()
    war_stats = []
    attacker_damage = []
    attacker_healing = []
    defender_damage = []
    defender_healing = []
    attacker_kills = []
    attacker_deaths = []
    attacker_assists = []

    defender_kills = []
    defender_deaths = []
    defender_assists = []
    war_winner = ""
    has_teams = False
    invasion_winner = myresult[0][10]
    for row in myresult:

        war_stats.append(row)
        print(row)

        defender_damage.append(int(row[9].replace("*","").replace("^","")))
        defender_kills.append(int(row[5].replace("*","").replace("^","")))
        defender_deaths.append(int(row[6].replace("*","").replace("^","")))
        defender_assists.append(int(row[7].replace("*","").replace("^","")))
        defender_healing.append(int(row[8].replace("*","").replace("^","")))
    print(war_stats)

    total_attacker_damage = 0
    total_defender_damage = sum(defender_damage)
    total_attacker_healing = 0
    total_defender_healing = sum(defender_healing)
    total_attacker_kills = 0
    total_defender_kills = sum(defender_kills)
    total_attacker_deaths = 0
    total_defender_deaths = sum(defender_deaths)
    total_attacker_assists = 0
    total_defender_assists = sum(defender_assists)
    attacker_dmg_per_kill = 0
    defender_dmg_per_kill = 0

    if str(sort_by) == 'kills':
        war_stats.sort(key = lambda x: int(x[5].replace("*","").replace("^","")), reverse = True)

        return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
    if str(sort_by) == 'deaths':
        war_stats.sort(key = lambda x: int(x[6].replace("*","").replace("^","")), reverse = True)

        return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
    if str(sort_by) == 'assists':
        war_stats.sort(key = lambda x: int(x[7].replace("*","").replace("^","")), reverse = True)

        return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
    if str(sort_by) == 'healing':
        war_stats.sort(key = lambda x: int(x[8].replace("*","").replace("^","")), reverse = True)

        return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
    if str(sort_by) == 'damage':
        war_stats.sort(key = lambda x: int(x[9].replace("*","").replace("^","")), reverse = True)

        return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
    if str(sort_by) == 'kpar':
        try:
            war_stats.sort(key = lambda x: float(x[11].replace("*","").replace("^","").replace(",","")), reverse = True)
            return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
        except ValueError:
            return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
    if str(sort_by) == 'dmgkpar':
        try:
            war_stats.sort(key = lambda x: int(float(x[12].replace("*","").replace("^","").replace(",",""))), reverse = True)
            return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
        except ValueError:
            return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
    if str(sort_by) == 'team':
        war_stats.sort(key = lambda x: x[13], reverse = True)

        return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
    if sort_by == "none":
        return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
    if str(sort_by) == 'role':
        try:
            war_stats.sort(key = lambda x: x[15], reverse = False)
            return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
        except ValueError:
            return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
    if sort_by == "none":
        print([war_stats])
        return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)



def search_war_results(searched_term):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # loop through the rows
    run_string = "SELECT * FROM player_records WHERE war_name LIKE %s"
    data = ('%' + searched_term + '%',)
    mycursor.execute(run_string,data)
    myresult = mycursor.fetchall()
    war_results = []
    wars = []
    for row in myresult:
        if searched_term.lower() in row[0].lower() and row[0] not in wars:
            war_results.append([row[0], row[9], row[16]])
            wars.append(row[0])
    return(war_results)

def remove_vod(removed_vod,war,server):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    sql = "DELETE FROM player_vods WHERE vod = %s AND server = %s AND war_id = %s"
    data = (removed_vod, server, war)
    mycursor.execute(sql,data)
    mydb.commit()
    sql = "DELETE FROM player_twitch_videos WHERE vod = %s AND server = %s AND war_id = %s"
    data = (removed_vod, server, war)
    mycursor.execute(sql,data)
    mydb.commit()
    sql = "DELETE FROM player_youtube_videos WHERE vod = %s AND server = %s AND war_id = %s"
    data = (removed_vod, server, war)
    mycursor.execute(sql,data)
    mydb.commit()

    return("Done!")


def setup_user_account(chosen_account):

    # Check to see if user account is already registered
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # loop through the rows
    mycursor.execute("SELECT * FROM player_accounts")
    myresult = mycursor.fetchall()
    found = False
    for row in myresult:
        if session['discord_id'] in row:
            sql = "UPDATE player_accounts SET default_profile = %s, header_color = %s, background_color = %s, scoreboard_color1 = %s, scoreboard_color2 = %s, scoreboard_text_color = %s, server = %s WHERE discord_id = %s"
            val = (chosen_account['player_name'], chosen_account['header_color'], chosen_account['background_color'], chosen_account['scoreboard_color1'], chosen_account['scoreboard_color2'], chosen_account['scoreboard_text_color'], chosen_account['server'], session['discord_id'])
            mycursor.execute(sql, val)
            mydb.commit()
            found = True
            break
    if found == False:
        data = (session['discord_id'], chosen_account['player_name'], chosen_account['header_color'], chosen_account['background_color'], chosen_account['scoreboard_color1'],chosen_account['scoreboard_color2'], chosen_account['scoreboard_text_color'])
        insert_stmt = (
        "INSERT INTO player_accounts(discord_id, default_profile, header_color, background_color, scoreboard_color1, scoreboard_color2, scoreboard_text_color)"
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        print(data)
        mycursor = mydb.cursor()
        mycursor.execute(insert_stmt, data)
        mydb.commit()



def reset_user_account(chosen_account):
    # Check to see if user account is already registered
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM player_accounts")
    mycursor.fetchall()
    sql = "UPDATE player_accounts SET default_profile = %s, header_color = %s, background_color = %s, scoreboard_color1 = %s, scoreboard_color2 = %s, scoreboard_text_color = %s, server = %s WHERE discord_id = %s"
    val = ('none','#6b0bb9','#212224', '#6b0bb9', '#24023f','white', "COS", chosen_account[0])
    mycursor.execute(sql, val)
    mydb.commit()






def search_player_results(searched_term):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # loop through the rows
    run_string = "SELECT * FROM player_records  WHERE name LIKE %s"
    data = ('%' + searched_term + '%',)
    mycursor.execute(run_string,data)
    myresult = mycursor.fetchall()
    player_results = []
    players = []
    for row in myresult:
        if searched_term.lower() in row[2].lower() and row[2] not in players:
            player_results.append([row[2],f"https://www.nw-stats.com/{row[16]}/player/{row[2]}"])
            players.append(row[2])
    return(player_results)



def get_record_wars(server):
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
    all_wars = []
    record_wars = []
    for row in myresult:
        if row[11] != "N/A" and row[16] == server:
            all_wars.append(row)
    record_wars = []
    all_wars.sort(key = lambda x: int(x[3].replace("*","")), reverse = True)
    record_score = all_wars[0]
    all_wars.sort(key = lambda x: int(x[4].replace("*","")), reverse = True)
    record_kills = all_wars[0]
    all_wars.sort(key = lambda x: int(x[5].replace("*","")), reverse = True)
    record_deaths = all_wars[0]
    all_wars.sort(key = lambda x: int(x[6].replace("*","")), reverse = True)
    record_assists = all_wars[0]
    all_wars.sort(key = lambda x: int(x[7].replace("*","")), reverse = True)
    record_healing = all_wars[0]
    all_wars.sort(key = lambda x: int(x[8].replace("*","")), reverse = True)
    record_damage = all_wars[0]
    all_wars.sort(key = lambda x: int(float(x[11].replace("*",""))), reverse = True)
    record_kpar = all_wars[0]
    record_wars = [record_kills,record_deaths,record_assists,record_healing,record_damage, record_score, record_kpar]
    return(record_wars)

def get_record_invasions(server):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # loop through the rows
    mycursor.execute("SELECT * FROM invasion_records")
    myresult = mycursor.fetchall()
    all_wars = []
    record_wars = []
    for row in myresult:
        if row[11] == server:
            all_wars.append(row)
    record_wars = []
    all_wars.sort(key = lambda x: int(x[4].replace("*","")), reverse = True)
    record_score = all_wars[0]
    all_wars.sort(key = lambda x: int(x[5].replace("*","")), reverse = True)
    record_kills = all_wars[0]
    all_wars.sort(key = lambda x: int(x[6].replace("*","")), reverse = True)
    record_deaths = all_wars[0]
    all_wars.sort(key = lambda x: int(x[7].replace("*","")), reverse = True)
    record_assists = all_wars[0]
    all_wars.sort(key = lambda x: int(x[8].replace("*","")), reverse = True)
    record_healing = all_wars[0]
    all_wars.sort(key = lambda x: int(x[9].replace("*","")), reverse = True)
    record_damage = all_wars[0]
    record_wars = [record_kills,record_deaths,record_assists,record_healing,record_damage, record_score, record_kpar]
    return(record_wars)

def get_war_list(page, server):
    war_list = []
    server = server.replace("_"," ")
    try:
        sh = gc.open(f'{server} war records')
        wks = sh.worksheet_by_title("War List")
        returned_values = wks.get_values_batch( ['A1:C1000'] )
        if page == 1:
            starting_war = 0
            ending_war = 10
        else:
            starting_war = (page*10)-10
            ending_war = (page*10)
        returned_values[0].reverse()
        war_list = returned_values[0][starting_war:ending_war]

        return(war_list)
    except:
        return([])

def get_invasion_list(page, server):
    war_list = []
    server = server.replace("_"," ")
    try:
        sh = gc.open(f'{server} invasion records')
        wks = sh.worksheet_by_title("Invasion List")
        returned_values = wks.get_values_batch( ['A1:C1000'] )
        if page == 1:
            starting_war = 0
            ending_war = 10
        else:
            starting_war = (page*10)-10
            ending_war = (page*10)
        returned_values[0].reverse()
        war_list = returned_values[0][starting_war:ending_war]

        return(war_list)
    except:
        return([])

def get_total_wars(page, server):

    pages_list = []
    server = server.replace("_"," ")
    try:
        sh = gc.open(f'{server} war records')
        wks = sh.worksheet_by_title("War List")
        returned_values = wks.get_values_batch( ['A1:C1000'] )
        total_wars = len(returned_values[0])
        pages = 0
        for o in returned_values[0][::10]:
            pages += 1
            pages_list.append(pages)
        if page >= 3:
            pages_list_shifted = pages_list[page-3:page+2]
            return(pages_list_shifted)
        else:
            return(pages_list[:5])
    except:
        return([])

def get_total_invasions(page, server):

    pages_list = []
    server = server.replace("_"," ")
    try:
        sh = gc.open(f'{server} invasion records')
        wks = sh.worksheet_by_title("War List")
        returned_values = wks.get_values_batch( ['A1:C1000'] )
        total_wars = len(returned_values[0])
        pages = 0
        for o in returned_values[0][::10]:
            pages += 1
            pages_list.append(pages)
        if page >= 3:
            pages_list_shifted = pages_list[page-3:page+2]
            return(pages_list_shifted)
        else:
            return(pages_list[:5])
    except:
        return([])


def get_total_wars_global():
    war_list = []
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    servers = get_all_servers_global()
    mycursor = mydb.cursor()
    # loop through the rows

    sql = "SELECT * FROM player_records"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for row in myresult:
        if [row[9],row[-1]] not in war_list:
            war_list.append([row[9],row[-1]])
    return(len(war_list))

def get_user_links(war_id):
    player_links = []
    sh = gc.open('Testing war dumps')
    wks = sh.worksheet_by_title(str(war_id))
    returned_values = wks.get_values_batch( ['A1:I105'] )
    for item in returned_values[0]:
        player_links.append(f'http://www.nw-stats.com/player/{item[1]}'.replace(" ", "%20"))
    return(player_links)

def get_war_title(war_id, server):
    sh = ""
    server = server.replace("_", " ")
    try:
        sh = gc.open(f'{server} war records')
        wks = sh.worksheet_by_title("War List")
        returned_values = wks.get_values_batch( ['A1:F1000'] )
        for item in returned_values[0]:
            if str(item[0]) == str(war_id):
                return([item[1],item[2],item[4],item[5],item[3]])
    except:
        return([])

def get_invasion_title(invasion_id, server):
    sh = ""
    server = server.replace("_", " ")
    try:
        sh = gc.open(f'{server} invasion records')
        wks = sh.worksheet_by_title("Invasion List")
        returned_values = wks.get_values_batch( ['A1:F1000'] )
        for item in returned_values[0]:
            if str(item[0]) == str(invasion_id):
                return([item[1],item[2],item[4],item[5],item[3]])
    except:
        return([])

def get_company_roster(comp):
    sh = gc.open('blacktunastats.com player responses')
    wks = sh.worksheet_by_title("Form Responses 1")
    returned_values = wks.get_values_batch( ['A2:E1000'] )
    print(comp.replace("%20", " ").lower())
    roster = []
    for item in returned_values[0]:
        print(item[4].lower())
        if comp.replace("%20", " ").lower() == item[4].lower():
            roster.append(item[1])

    return(roster)

def get_player_info(usr):
    sh = gc.open('blacktunastats.com player responses')
    wks = sh.worksheet_by_title("Form Responses 1")
    returned_values = wks.get_values_batch( ['A2:E1000'] )
    for item in returned_values[0]:
        if usr.lower() == item[1].lower():
            found = True
            return([item[2],item[3],item[4]])

def get_player_logo(player_name):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # loop through the rows
    sql = "SELECT * FROM player_info WHERE player_name = %s"
    val = (player_name,)
    mycursor.execute(sql,val)
    myresult = mycursor.fetchall()

    for row in myresult:
        if row[0].lower() == player_name.lower() and row[4] != None:
            return(row[4])
    return("/static/images/pfp.png")

def get_player_entered_info(player_name):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # loop through the rows
    sql = "SELECT * FROM player_info WHERE player_name = %s"
    val = (player_name,)
    mycursor.execute(sql,val)
    myresult = mycursor.fetchall()

    for row in myresult:
        if row[0].lower() == player_name.lower():
            print(row)
            return(row)

def get_player_settings():
    if session['discord_id'] != "":
        mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
        )
        mycursor = mydb.cursor()
        # loop through the rows
        sql = "SELECT * FROM player_accounts WHERE discord_id = %s"
        val = (session['discord_id'],)
        mycursor.execute(sql,val)
        myresult = mycursor.fetchall()
        for row in myresult:
            if int(row[0]) == int(session['discord_id']):
                return(row)
        return(['1','none','#6b0bb9','#212224', '#6b0bb9', '#24023f','white',"","False",""])
    else:
        return(['1','none','#6b0bb9','#212224', '#6b0bb9', '#24023f','white',"","False",""])

def get_selected_war(war_id, usr):
    player_settings = get_player_settings()
    selected_war = ''
    if session['discord_id'] != "" and usr == "":
        mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
        )
        mycursor = mydb.cursor()
        # loop through the rows
        sql = "SELECT * FROM player_records WHERE war_id = %s AND name=%s"
        val = (war_id, player_settings[8])
        mycursor.execute(sql,val)
        mywarresult = mycursor.fetchall()

    if session['discord_id'] != "" and player_settings[8].lower().__contains__(usr.lower()):
        mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
        )
        mycursor = mydb.cursor()
        # loop through the rows
        sql = "SELECT * FROM player_records WHERE war_id = %s AND name=%s"
        val = (war_id, usr)
        mycursor.execute(sql,val)
        mywarresult = mycursor.fetchall()


    for row in mywarresult:
        if (player_settings[7] == "True"):
            selected_war = row
            return(selected_war)

def set_war_role(usr,war_id,role,server):
    player_settings = get_player_settings()
    # Check to see if user account is already registered
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    if player_settings[8].lower().__contains__(usr.lower()):
        sql = "UPDATE player_records SET player_role = %s WHERE war_id = %s AND name = %s AND server = %s"
        val = (role, war_id, usr, server)

        mycursor.execute(sql, val)

        mydb.commit()

        if mycursor.rowcount == 1:
            return("Your role has been updated for this war! Thank you for helping to improve the quality and accuracy of the stats on this site!")
        else:
            return("We could not update your role for this war, please try again later, if this happens repeatedly, please contact Superdotaplaya for help!")


def compare_player_stats_to_role(role_stats,player_stats):
    print(role_stats)
    print(player_stats)
    player_avg_score = float(player_stats[0])
    player_avg_kills = float(player_stats[1])
    player_avg_deaths = float(player_stats[2])
    player_avg_assists = float(player_stats[3])
    player_avg_healing = float(player_stats[4])
    player_avg_damage =float(player_stats[5])
    player_healing_per_death = float(player_stats[6])
    player_damage_per_death =  float(player_stats[7])
    player_assists_per_death = float(player_stats[11])
    player_kills_plus_assists_per_death = float(player_stats[18])
    player_kills_per_death = float(player_stats[17])
    role_avg_score = float(role_stats[0])
    role_avg_kills = float(role_stats[1])
    role_avg_deaths = float(role_stats[2])
    role_avg_assists = float(role_stats[3])
    role_avg_healing = float(role_stats[4])
    role_avg_damage = float(role_stats[5])
    role_healing_per_death = float(role_stats[6])
    role_damage_per_death = float(role_stats[7])
    role_assists_per_death = float(role_stats[11])
    role_kills_plus_assists_per_death = float(role_stats[18])
    role_kills_per_death = float(role_stats[17])

    # Differential calculation to determine difference between player stats and role stats

    avg_score_diff = player_avg_score - role_avg_score
    avg_kills_diff = player_avg_kills - role_avg_kills
    avg_deaths_diff = player_avg_deaths - role_avg_deaths
    avg_assists_diff = player_avg_assists - role_avg_assists
    avg_healing_diff = player_avg_healing - role_avg_healing
    avg_damage_diff = player_avg_damage - role_avg_damage
    healing_per_death_diff = player_healing_per_death - role_healing_per_death
    damage_per_death_diff = player_damage_per_death - role_damage_per_death
    assists_per_death_diff = player_assists_per_death - role_assists_per_death
    kills_plus_assists_per_death_diff = player_kills_plus_assists_per_death - role_kills_plus_assists_per_death
    kills_per_death_diff = player_kills_per_death - role_kills_per_death
    print(avg_score_diff,avg_kills_diff,avg_deaths_diff,avg_assists_diff,avg_healing_diff,avg_damage_diff, healing_per_death_diff, damage_per_death_diff,assists_per_death_diff,kills_plus_assists_per_death_diff,kills_per_death_diff)
    return("{:.2f}".format(avg_score_diff),"{:.2f}".format(avg_kills_diff),"{:.2f}".format(avg_deaths_diff),"{:.2f}".format(avg_assists_diff),"{:.2f}".format(avg_healing_diff),"{:.2f}".format(avg_damage_diff), "{:.2f}".format(healing_per_death_diff), "{:.2f}".format(damage_per_death_diff),"{:.2f}".format(assists_per_death_diff),"{:.2f}".format(kills_plus_assists_per_death_diff),"{:.2f}".format(kills_per_death_diff))


def get_submitted_vods(war_id, server):
    clips = []
    twitch_vods = []
    youtube_vods = []
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # loop through the rows
    sql = "SELECT * FROM player_vods WHERE war_id = %s AND server = %s"
    data = (war_id, server)
    mycursor.execute(sql,data)
    all_clips = mycursor.fetchall()
    sql = "SELECT * FROM player_twitch_videos WHERE war_id = %s AND server = %s"
    data = (war_id, server)
    mycursor.execute(sql,data)
    all_twitch_vods = mycursor.fetchall()
    sql = "SELECT * FROM player_youtube_videos WHERE war_id = %s AND server = %s"
    data = (war_id, server)
    mycursor.execute(sql,data)
    all_youtube_vods = mycursor.fetchall()

    for item in all_clips:
        clips.append(item)
        print(item)
    for item in all_twitch_vods:
        twitch_vods.append(item)
        print(item)
    for item in all_youtube_vods:
        youtube_vods.append(item)
    return(clips,twitch_vods,youtube_vods)

def submit_vod(war_id,vod,desc,server):
    found = False
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    data = (war_id,vod,desc, server)


    if "https://clips.twitch.tv/" in vod:
        new_vod = vod.replace("https://clips.twitch.tv/","")
        mycursor.execute("SELECT * FROM player_vods")
        myresult = mycursor.fetchall()
        for item in myresult:
            if item[1] == new_vod and item[0] == war_id and item[3].lower() == server.lower():
                found = True

        if found == False:

            data = (war_id,new_vod,desc,server)
            insert_stmt = (
                    "INSERT INTO player_vods(war_id, vod, description, server)"
                    "VALUES (%s, %s, %s, %s)"
                    )
            print(data)
            mycursor.execute(insert_stmt, data)
            mydb.commit()
            return("Your vod has been submitted, go back to the war page to view the clip in the collection!")
        else:
            return("The clip you submitted has previously been submitted by another user!")

    elif "https://www.twitch.tv/videos/" in vod:
        new_vod = vod.replace("https://www.twitch.tv/videos/","")
        mycursor.execute("SELECT * FROM player_twitch_videos")
        myresult = mycursor.fetchall()
        for item in myresult:
            if item[1] == new_vod and item[0] == war_id and item[3].lower() == server.lower():
                found = True

        if found == False:

            data = (war_id,new_vod, desc, server)
            insert_stmt = (
                    "INSERT INTO player_twitch_videos(war_id, vod, description, server)"
                    "VALUES (%s, %s, %s, %s)"
                    )
            print(data)
            mycursor.execute(insert_stmt, data)
            mydb.commit()
            return("Your vod has been submitted, go back to the war page to view the clip in the collection!")
        else:
            return("The clip you submitted has previously been submitted by another user!")
    elif "https://www.youtube.com/watch?v" in vod or "https://m.youtube.com/watch?v" in vod:
        new_vod = vod.replace("https://www.youtube.com/watch?v=","").replace("https://m.youtube.com/watch?v=","")
        mycursor.execute("SELECT * FROM player_youtube_videos")
        myresult = mycursor.fetchall()
        for item in myresult:
            if item[1] == new_vod and item[0] == war_id and item[3].lower() == server.lower():
                found = True

        if found == False:

            data = (war_id,new_vod,desc, server)
            insert_stmt = (
                    "INSERT INTO player_youtube_videos(war_id, vod, description, server)"
                    "VALUES (%s, %s, %s, %s)"
                    )
            print(data)
            mycursor.execute(insert_stmt, data)
            mydb.commit()
            return("Your vod has been submitted, go back to the war page to view the clip in the collection!")
        else:
            return("The clip you submitted has previously been submitted by another user!")
    else:
        return("We are unable to submit your clip, please ensure it is a twitch clip, we are looking to enable the submission of other platforms such as youtube, but for the time being only twitch clips are permitted! If the clip has been submitted by someone else, it cannot be submitted again!")

def submit_vod_player(player,vod,desc, server):
    found = False
    player_settings = get_player_settings()
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    data = (player,vod,desc)

    if player_settings[8].lower().__contains__(player.lower()):
        if "https://clips.twitch.tv/" in vod:
            new_vod = vod.replace("https://clips.twitch.tv/","")
            mycursor.execute("SELECT * FROM player_vods")
            myresult = mycursor.fetchall()
            for item in myresult:
                if item[1] == new_vod and item[0] == player and item[3].lower() == server.lower():
                    found = True

            if found == False:

                data = (player,new_vod,desc, server)
                insert_stmt = (
                        "INSERT INTO player_vods(war_id, vod, description, server)"
                        "VALUES (%s, %s, %s, %s)"
                        )
                print(data)
                mycursor.execute(insert_stmt, data)
                mydb.commit()
                return("Your vod has been submitted, go back to the war page to view the clip in the collection!")
            else:
                return("The clip you submitted has previously been submitted by another user!")

        elif "https://www.twitch.tv/videos/" in vod:
            new_vod = vod.replace("https://www.twitch.tv/videos/","")
            mycursor.execute("SELECT * FROM player_twitch_videos")
            myresult = mycursor.fetchall()
            for item in myresult:
                if item[1] == new_vod and item[0] == player and item[3].lower() == server.lower():
                    found = True

            if found == False:

                data = (player,new_vod, desc, server)
                insert_stmt = (
                        "INSERT INTO player_twitch_videos(war_id, vod, description, server)"
                        "VALUES (%s, %s, %s, %s)"
                        )
                print(data)
                mycursor.execute(insert_stmt, data)
                mydb.commit()
                return("Your vod has been submitted, go back to the war page to view the clip in the collection!")
            else:
                return("The clip you submitted has previously been submitted by another user!")
        elif "https://www.youtube.com/watch?v" in vod or "https://m.youtube.com/watch?v" in vod:
            new_vod = vod.replace("https://www.youtube.com/watch?v=","").replace("https://m.youtube.com/watch?v=","")
            mycursor.execute("SELECT * FROM player_youtube_videos")
            myresult = mycursor.fetchall()
            for item in myresult:
                if item[1] == new_vod and item[0] == player and item[3].lower() == server.lower():
                    found = True

            if found == False:

                data = (player,new_vod, desc, server)
                insert_stmt = (
                        "INSERT INTO player_youtube_videos(war_id, vod, description, server)"
                        "VALUES (%s, %s, %s, %s)"
                        )
                print(data)
                mycursor.execute(insert_stmt, data)
                mydb.commit()
                return("Your vod has been submitted, go back to the war page to view the clip in the collection!")
            else:
                return("The clip you submitted has previously been submitted by another user!")
        else:
            return("We are unable to submit your clip, please ensure it is a twitch clip, vod, or youtube video! If the Vod has been submitted already, it cannot be submitted again!")
    else:
        return("""This account is either not verified, or you are not the owner of this character, to verify your account, go to Settings > "Verify Account" and follow the instructions in that discord channel! If you beleive this is an error, please try again or reach out for help!""")


def get_player_role_stats(player,player_role, server):
    print(player,player_role)
    role = player_role
    player_results = []
    player_score = []
    player_kills = []
    player_deaths = []
    player_assists = []
    player_healing = []
    player_damage = []
    player_kpars = []
    wins = []
    losses = []
    roles_played = []



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



    for row in myresult:
        if row[2].lower() == player.lower() and server == row[16].lower() and row[16].lower() == server.lower():
            roles_played.append(row[15].lower())
        if row[2].lower() == player.lower() and row[15].lower() == role.lower() and row[16].lower() == server.lower():

            player_results.append(row)
            if row[13] == row[14] and row[14] != "N/A" and row[13] != "N/A" and row[16].lower() == server.lower():
                wins.append(row)
            elif row[13] != row[14] and row[14] != "N/A" and row[13] != "N/A" and row[16].lower() == server.lower():
                losses.append(row)


    for player_entry in player_results:

        player_results.sort(key = lambda x: int(x[4].replace("*","").replace("^","")), reverse = True)
    max_kill_war = player_results[0][0]
    player_results.sort(key = lambda x: int(x[7].replace("*","").replace("^","")), reverse = True)
    max_healing_war = player_results[0][0]
    player_results.sort(key = lambda x: int(x[8].replace("*","").replace("^","")), reverse = True)
    max_damage_war = player_results[0][0]
    player_results.sort(key = lambda x: int(x[6].replace("*","").replace("^","")), reverse = True)
    max_assists_war = player_results[0][0]
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


    def get_healing_graph(player_healing):

        x_axis = range(1,len(player_healing)+1)
        x = x_axis[:]
        y = player_healing[:]
        fig, ax = plt.subplots()
        ax.grid(True, alpha=0.3)

        N = len(player_healing)
        df = pd.DataFrame(index=range(N))
        df['x'] = x
        df['y'] = y

        labels = []
        for i in range(N):
            label = df.iloc[[i], :].T
            label.columns = ['Row {0}'.format(i)]
            # .to_html() is unicode; so make leading 'u' go away with str()
            labels.append(str(label.to_html()))

        boxes = ax.bar(x,y)

        ax.set_xlabel('War Number')
        ax.set_ylabel('Healing Amount')
        ax.set_title('Healing Performance', size=20)
        plt.figure(figsize=(3,2))

        for i, box in enumerate(boxes.get_children()):
            tooltip = mpld3.plugins.LineLabelTooltip(box, label=f"{y[i]} Healing")
            mpld3.plugins.connect(fig, tooltip)
        plugins.connect(fig, tooltip)

        return(mpld3.fig_to_html(fig))


    def get_damage_graph(player_damage):

        x_axis = range(1,len(player_damage)+1)
        x = x_axis[:]
        y = player_damage[:]
        fig, ax = plt.subplots()
        ax.grid(True, alpha=0.3)

        N = len(player_damage)
        df = pd.DataFrame(index=range(N))
        df['x'] = x
        df['y'] = y

        labels = []
        for i in range(N):
            label = df.iloc[[i], :].T
            label.columns = ['Row {0}'.format(i)]
            labels.append(str(label.to_html()))

        boxes = ax.bar(x,y)

        ax.set_xlabel('War Number')
        ax.set_ylabel('Damage Amount')
        ax.set_title('Damage Performance', size=20)

        for i, box in enumerate(boxes.get_children()):
            tooltip = mpld3.plugins.LineLabelTooltip(box, label=f"{y[i]} Damage")
            mpld3.plugins.connect(fig, tooltip)
        plugins.connect(fig, tooltip)

        return(mpld3.fig_to_html(fig))

    player_stats = ["{:.2f}".format(avg_score),"{:.2f}".format(avg_kills),"{:.2f}".format(avg_deaths),"{:.2f}".format(avg_assists),"{:.2f}".format(avg_healing),"{:.2f}".format(avg_damage), "{:.2f}".format(healing_per_death), "{:.2f}".format(damage_per_death), max_kills, max_healing, max_damage, "{:.2f}".format(assists_per_death), total_kills, total_deaths, total_assists, total_damage, total_healing, "{:.2f}".format(kills_plus_assists_per_death),"{:.2f}".format(kills_per_death),0,0,max_healing_war,max_kill_war,max_assists_war,max_damage_war, max_assists, total_wins, total_losses, "{:.2f}".format(average_kpar), roles_played, total_wins + total_losses]

    return(player_stats)




def get_servers_played(player):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # loop through the rows
    sql ="SELECT * FROM player_records WHERE name = %s"
    data = (player,)
    mycursor.execute(sql,data)
    myresult = mycursor.fetchall()
    servers_played = []
    for item in myresult:
        if item[16] not in servers_played and item[2].lower() == player.lower():
            servers_played.append(item[16])
    return(servers_played)



@app.before_request
def make_session_permanent():
    session.permanent = True
    try:
        test = session['discord_id']
    except:
        session['discord_id'] = ""
        session['logged_in'] = False
        session['has_ads'] = True

@app.route("/<server>")
def home(server):
    page = 1
    return render_template("index.html", content = "Testing", war_list = get_war_list(page, server)[:10], pages = get_total_wars(1,server)[:], logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route, server = server)

@app.route("/<server>/invasions")
def home_invasions(server):
    page = 1
    return render_template("invasion_index.html", content = "Testing", war_list = get_invasion_list(page, server)[:10], pages = get_total_invasions(1,server)[:], logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route, server = server)

@app.route("/<server>/invasions/<page_num>")
def home_invasions_pages(page_num, server):
    if page_num == "first":
        page = 1
        return render_template("index.html", content = "Testing", war_list = get_invasion_list(page, server)[:10], pages = get_total_invasions(page, server)[:], logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), server = server
    )
    elif page_num == "last":
        pages_list = []
        sh = gc.open('Testing war dumps')
        wks = sh.worksheet_by_title("War List")
        returned_values = wks.get_values_batch( ['A1:C1000'] )
        total_invasions = len(returned_values[0])
        pages = 0
        for o in returned_values[0][::10]:
            pages += 1
            pages_list.append(pages)
        page = max(pages_list)
        return render_template("index.html", content = "Testing", war_list = get_war_list(page, server)[:10], pages = get_total_wars(page, server)[:], logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), server = server
    )

    else:
        page = int(page_num)
        return render_template("index.html", content = "Testing", war_list = get_war_list(page, server)[:10], pages = get_total_wars(page, server)[:], logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), server = server
    )
@app.route("/<server>/roles")
def roles(server):
    return render_template("roles.html", content = "Testing",logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route, server = server
)

@app.route("/<server>/<page_num>")
def home_pages(page_num, server):
    if page_num == "first":
        page = 1
        return render_template("index.html", content = "Testing", war_list = get_war_list(page, server)[:10], pages = get_total_wars(page, server)[:], logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), server = server
    )
    elif page_num == "last":
        pages_list = []
        sh = gc.open('Testing war dumps')
        wks = sh.worksheet_by_title("War List")
        returned_values = wks.get_values_batch( ['A1:C1000'] )
        total_wars = len(returned_values[0])
        pages = 0
        for o in returned_values[0][::10]:
            pages += 1
            pages_list.append(pages)
        page = max(pages_list)
        return render_template("index.html", content = "Testing", war_list = get_war_list(page, server)[:10], pages = get_total_wars(page, server)[:], logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), server = server
    )

    else:
        page = int(page_num)
        return render_template("index.html", content = "Testing", war_list = get_war_list(page, server)[:10], pages = get_total_wars(page, server)[:], logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), server = server
    )



@app.route("/<server>/invasion/<invasion_id>", methods=["POST", "GET"])
def invasion(server, invasion_id):
    if request.method == "POST":
        invasion_requested = request.form["invasion"]

        return render_template("invasions.html",info = get_invasion_stats(invasion_id,'none', server), war_title = get_invasion_title(war_requested, server), logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
    , war_id = invasion_id, vods = get_submitted_vods(invasion_id, server), server = server)
    else:
        print(get_invasion_stats(invasion_id,'none', server))
        return render_template("invasions.html", info= get_invasion_stats(invasion_id, 'none', server)[:], war_title = get_invasion_title(invasion_id, server), war_link = invasion_id, sorted_by = "none", logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
    , war_id = invasion_id, vods = get_submitted_vods(invasion_id, server), server = server)

@app.route("/<server>/war/<war_id>", methods=["POST", "GET"])
def war(server, war_id):
    return render_template("war.html", info= get_war_stats(war_id,'none', server), war_title = get_war_title(war_id, server), war_link = war_id, sorted_by = "none", logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
, vods = get_submitted_vods(war_id, server), server = server, group_stats = get_group_stats(war_id,server))

@app.route("/<server>/war/<war_id>/<sort_by>", methods=["POST", "GET"])
def war_sorted(server, war_id,sort_by):
    return render_template("war.html", info= get_war_stats(war_id,str(sort_by), server), war_title = get_war_title(war_id, server), war_link = war_id, sorted_by = sort_by, logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
, vods = get_submitted_vods(war_id, server), server = server)

@app.route("/<server>/invasion/<invasion_id>/<sort_by>", methods=["POST", "GET"])
def invasion_sorted(server, invasion_id,sort_by):
    return render_template("invasions.html", info= get_invasion_stats(invasion_id,str(sort_by), server), war_title = get_invasion_title(invasion_id, server), war_id = invasion_id, sorted_by = sort_by, logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
, vods = get_submitted_vods(invasion_id, server), server = server)

@app.route("/<server>/compare/role/<role>/<usr>", methods=["POST", "GET"])
def compare_stats(role,usr, server):
        return render_template("player_vs_role.html", info= get_player_role_stats(usr,role,server), war_logs=sql_stuff.get_user_wars(usr, role, server), role = role, player = usr, player_info = get_player_entered_info(user), logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
    , role_stats = sql_stuff.get_role_stats(role, server), compare_role_stats = compare_player_stats_to_role(sql_stuff.get_role_stats(role, server), get_player_role_stats(usr,role, server)), vods = get_submitted_vods(usr, server), server = server)

@app.route("/verification")
def player_verification():
    return render_template("player_verification.html", logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
)


@app.route("/<server>/player/<usr>")
def user(usr, server):
    player = usr
    role = "All"
    servers_played = get_servers_played(usr)
    player_gear = get_player_gear(player)
    return render_template("player_stats.html", info= sql_stuff.calc_stats(usr,server), war_logs=sql_stuff.get_user_wars(usr, role, server), role = role, player = usr, player_info = get_player_entered_info(usr), logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
, vods = get_submitted_vods(player, server), server = server, servers_played = servers_played, player_logo = get_player_logo(usr), player_gear = player_gear, servers = get_servers_played(usr), all_servers = get_all_servers_global())

@app.route("/<server>/player/<usr>/invasions")
def user_invasions(usr, server):
    player = usr
    role = "All"
    servers_played = get_servers_played(usr)
    player_gear = get_player_gear(player)
    return render_template("player_stats.html", info= sql_stuff.calc_stats_invasions(usr,server), war_logs=sql_stuff.get_user_invasions(usr, role, server), role = role, player = usr, player_info = get_player_entered_info(usr), logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
, vods = get_submitted_vods(player, server), server = server, servers_played = servers_played, player_logo = get_player_logo(usr), player_gear = player_gear, servers = get_servers_played(usr), all_servers = get_all_servers_global())

@app.route("/<server>/player/<usr>/<player_role>")
def user_role_stats(usr,player_role, server):
    print(usr)
    print(player_role)
    info = get_player_role_stats(usr,player_role, server)
    servers_played = get_servers_played(usr)
    player_gear = get_player_gear(usr)
    return render_template("player_stats.html", info= info, war_logs=sql_stuff.get_user_wars_role(usr,player_role, server), player = usr, role = player_role, player_info = get_player_entered_info(usr), logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
, vods = get_submitted_vods(usr, server), server = server, servers_played = servers_played, player_logo = get_player_logo(usr), player_gear = player_gear, all_servers = get_all_servers_global())


@app.route("/<server>/update_role/<usr>/<war_id>", methods = ['POST', 'GET'])
def enter_role(server,usr,war_id):
    if request.method == "POST":
        role = request.form['role_played']
        message = set_war_role(usr,war_id,role,server)

        return render_template("enter_role_info.html", player = usr, logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
    , selected_war = get_selected_war(war_id, usr), war_id = war_id, message = message, server = server, player_logo = get_player_logo(usr), all_servers = get_all_servers_global())
    else:
        return render_template("enter_role_info.html", player = usr, logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
    , selected_war = get_selected_war(war_id, usr), war_id = war_id, message = "", server = server, player_logo = get_player_logo(usr))

@app.route("/<server>/war/<war_id>/submit_clip", methods = ['POST','GET'])
def submit_vod_page(war_id, server):
    if request.method == "POST":
        vod = request.form['submitted_vod']
        desc = request.form['submitted_vod_desc']
        if vod != "":
            vod_submission = submit_vod(war_id,vod,desc,server)
            usr = ""
            return render_template("submit_clip_or_vod.html",logged_in = is_logged_in(),has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
        , war_id = war_id, message = vod_submission, selected_war = get_selected_war(war_id, usr), war_title = get_war_title(war_id, server), server = server)
    if request.method == "GET":
        return render_template("submit_clip_or_vod.html",logged_in = is_logged_in(),has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
    , war_id = war_id, message = "", war_title = get_war_title(war_id, server), server = server)

@app.route("/<server>/player/<player>/submit_clip", methods = ['POST','GET'])
def submit_vod_page_player(server, player):
    if request.method == "POST":
        vod = request.form['submitted_vod']
        desc = request.form['submitted_vod_desc']
        if vod != "":
            vod_submission = submit_vod_player(player,vod,desc, server)
            return render_template("player_enter_vod.html",logged_in = is_logged_in(),has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
        , player = player, message = vod_submission, server = server)
    if request.method == "GET":
        return render_template("player_enter_vod.html",logged_in = is_logged_in(),has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
    , player = player, message = "", server = server)

def get_group_stats(war_id,server):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # Get all the players o9n the attacking side for the war.
    sql ="SELECT * FROM group_records WHERE war_id = %s AND server = %s AND group_team = %s"
    data = (war_id, server, "Attack")
    mycursor.execute(sql,data)
    myresult_attack = mycursor.fetchall()

    ## Get all the players on the defending side for the war.
    sql ="SELECT * FROM group_records WHERE war_id = %s AND server = %s AND group_team = %s"
    data = (war_id, server, "Defense")
    mycursor.execute(sql,data)
    myresult_defense = mycursor.fetchall()

    group1 = []
    group2 = []
    group3 = []
    group4 = []
    group5 = []
    group6 = []
    group7 = []
    group8 = []
    group9 = []
    group10 = []
    group11 = []
    group12 = []
    group13 = []
    group14 = []
    group15 = []
    group16 = []
    group17 = []
    group18 = []
    group19 = []
    group20 = []
    group1stats = []
    group2stats = []
    group3stats = []
    group4stats = []
    group5stats = []
    group6stats = []
    group7stats = []
    group8stats = []
    group9stats = []
    group10stats = []
    group11stats = []
    group12stats = []
    group13stats = []
    group14stats = []
    group15stats = []
    group16stats = []
    group17stats = []
    group18stats = []
    group19stats = []
    group20stats = []
## Checks what group each player is in, and puts them into the correct group for the tables on the war html page

    ## Places the players in their proper attackers groups
    for item in myresult_attack:
        if item[1] == "1":
            group1.append(item[0])
        if item[1] == "2":
            group2.append(item[0])
        if item[1] == "3":
            group3.append(item[0])
        if item[1] == "4":
            group4.append(item[0])
        if item[1] == "5":
            group5.append(item[0])
        if item[1] == "6":
            group6.append(item[0])
        if item[1] == "7":
            group7.append(item[0])
        if item[1] == "8":
            group8.append(item[0])
        if item[1] == "9":
            group9.append(item[0])
        if item[1] == "10":
            group10.append(item[0])

    ## Places the players in their proper defenders groups
    for item in myresult_defense:
        if item[1] == "1":
            group11.append(item[0])
        if item[1] == "2":
            group12.append(item[0])
        if item[1] == "3":
            group13.append(item[0])
        if item[1] == "4":
            group14.append(item[0])
        if item[1] == "5":
            group15.append(item[0])
        if item[1] == "6":
            group16.append(item[0])
        if item[1] == "7":
            group17.append(item[0])
        if item[1] == "8":
            group18.append(item[0])
        if item[1] == "9":
            group19.append(item[0])
        if item[1] == "10":
            group20.append(item[0])
    war_stats = get_war_stats(war_id,'none', server)

## Gets the players stats from the database from the war, and adds their stats for this war to a list to be used to display the players stats in the groups table on the war scoreboard page.
    for item in war_stats[0][0]:
        if item[2] in group1:
            group1stats.append(item)
        if item[2] in group2:
            group2stats.append(item)
        if item[2] in group3:
            group3stats.append(item)
        if item[2] in group4:
            group4stats.append(item)
        if item[2] in group5:
            group5stats.append(item)
        if item[2] in group6:
            group6stats.append(item)
        if item[2] in group7:
            group7stats.append(item)
        if item[2] in group8:
            group8stats.append(item)
        if item[2] in group9:
            group9stats.append(item)
        if item[2] in group10:
            group10stats.append(item)
        if item[2] in group11:
            group11stats.append(item)
        if item[2] in group12:
            group12stats.append(item)
        if item[2] in group13:
            group13stats.append(item)
        if item[2] in group14:
            group14stats.append(item)
        if item[2] in group15:
            group15stats.append(item)
        if item[2] in group16:
            group16stats.append(item)
        if item[2] in group17:
            group17stats.append(item)
        if item[2] in group18:
            group18stats.append(item)
        if item[2] in group19:
            group19stats.append(item)
        if item[2] in group20:
            group20stats.append(item)
    i = 1

## Fills gaps in tables with empty rows to ensure tables are equal size, and its clear that players are missing from the group for some reason.
    while i <= 5:
        if len(group1stats) < 5:
            group1stats.append(["N/A",0,"N/A",0,0,0,0,0,0,0,0,0,0])
        if len(group2stats) < 5:
            group2stats.append(["N/A",0,"N/A",0,0,0,0,0,0,0,0,0,0])
        if len(group3stats) < 5:
            group3stats.append(["N/A",0,"N/A",0,0,0,0,0,0,0,0,0])
        if len(group4stats) < 5:
            group4stats.append(["N/A",0,"N/A",0,0,0,0,0,0,0,0,0])
        if len(group5stats) < 5:
            group5stats.append(["N/A",0,"N/A",0,0,0,0,0,0,0,0,0,0])
        if len(group6stats) < 5:
            group6stats.append(["N/A",0,"N/A",0,0,0,0,0,0,0,0,0])
        if len(group7stats) < 5:
            group7stats.append(["N/A",0,"N/A",0,0,0,0,0,0,0,0,0])
        if len(group8stats) < 5:
            group8stats.append([0,0,"N/A",0,0,0,0,0,0,0,0,0])
        if len(group9stats) < 5:
            group9stats.append([0,0,"N/A",0,0,0,0,0,0,0,0,0])
        if len(group10stats) < 5:
            group10stats.append([0,0,"N/A",0,0,0,0,0,0,0,0,0])
        if len(group11stats) < 5:
            group11stats.append(["N/A",0,"N/A",0,0,0,0,0,0,0,0,0,0])
        if len(group12stats) < 5:
            group12stats.append(["N/A",0,"N/A",0,0,0,0,0,0,0,0,0,0])
        if len(group13stats) < 5:
            group13stats.append(["N/A",0,"N/A",0,0,0,0,0,0,0,0,0])
        if len(group14stats) < 5:
            group14stats.append(["N/A",0,"N/A",0,0,0,0,0,0,0,0,0])
        if len(group15stats) < 5:
            group15stats.append(["N/A",0,"N/A",0,0,0,0,0,0,0,0,0,0])
        if len(group16stats) < 5:
            group16stats.append(["N/A",0,"N/A",0,0,0,0,0,0,0,0,0])
        if len(group17stats) < 5:
            group17stats.append(["N/A",0,"N/A",0,0,0,0,0,0,0,0,0])
        if len(group18stats) < 5:
            group18stats.append([0,0,"N/A",0,0,0,0,0,0,0,0,0])
        if len(group19stats) < 5:
            group19stats.append([0,0,"N/A",0,0,0,0,0,0,0,0,0])
        if len(group20stats) < 5:
            group20stats.append([0,0,"N/A",0,0,0,0,0,0,0,0,0])
        i += 1

    ## Group 1-10 are attackers and groups 11-20 are defenders groups.
    return(group1stats,group2stats,group3stats,group4stats,group5stats,group6stats,group7stats,group8stats,group9stats,group10stats,group11stats,group12stats,group13stats,group14stats,group15stats,group16stats,group17stats,group18stats,group19stats,group20stats)

@app.route("/<server>/player/<usr>/wars")
def user_wars(usr, server):
    role = "All"
    return render_template("all_wars.html", info= sql_stuff.calc_stats(usr, server), war_logs=sql_stuff.get_user_wars(usr, role, server), player = usr, player_info = get_player_entered_info(usr), logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
, war_vods = get_submitted_vods(usr, server), server = server, all_servers = get_all_servers_global())


@app.route("/company/<comp>")
def company(comp):
    return render_template("company_info.html", roster = get_company_roster(comp), company_name = comp, logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route, server = ""
)

@app.route("/player_info")
def update_player_info():
    return redirect("https://forms.gle/87h5ydkkR5A8pbR17")

@app.route('/search', methods = ['POST', 'GET'])
def search():
    server = ""
    if request.method == 'GET':
        return render_template('search.html',form_data="", search_term = "", logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route, server = server, results = [])
    if request.method == 'POST':
        print(request.form)
        form_data = request.form
        search_term = form_data['searched_term']
        return(render_template('search.html',form_data = form_data, player_results = search_player_results(search_term), war_results= search_war_results(search_term), searched_term = search_term, logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route, server = server, results = []
    ))

@app.route("/<server>/records")
def records(server):
    return render_template("records.html", record_wars = get_record_wars(server), logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route, server = server
)
# Discord login for ad free browsing
@app.route("/login")
def login():
    """
    Presents the 'Login with Discord' link
    """
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    login_url, state = oauth.authorization_url(authorize_url)
    session['state'] = state
    print("Login url: %s" % login_url)
    return redirect(login_url)

@app.route("/oauth_callback")
def oauth_callback():
    """
    The callback we specified in our app.
    Processes the code given to us by Discord and sends it back
    to Discord requesting a temporary access token so we can
    make requests on behalf (as if we were) the user.
    e.g. https://discordapp.com/api/users/@me
    The token is stored in a session variable, so it can
    be reused across separate web requests.
    """
    discord = OAuth2Session(client_id, redirect_uri=redirect_uri, state=session['state'], scope=scope)
    token = discord.fetch_token(
        token_url,
        client_secret=client_secret,
        authorization_response=request.url,
    )
    session['discord_token'] = token
    discord = OAuth2Session(client_id, token=session['discord_token'])
    response = discord.get(base_discord_api_url + '/users/@me/guilds/892232759513350174/member')
    response2 = discord.get(base_discord_api_url + '/users/@me')
    session['discord_id'] = response2.json()['id']
    player_logo = f"https://cdn.discordapp.com/avatars/{session['discord_id']}/{response2.json()['avatar']}.jpg"
    print(player_logo)
    player_settings = get_player_settings()
    if player_settings[0] == '1':
        chosen_account = {'discord_id':response2.json()['id'],
        'player_name':'none',
        'header_color':'#6b0bb9',
        'background_color':'#212224',
        'scoreboard_color1':'#6b0bb9',
        'scoreboard_color2':'#24023f',
        'scoreboard_text_color':'white'
                 }
        mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
            )
        data = (session['discord_id'], chosen_account['player_name'], chosen_account['header_color'], chosen_account['background_color'], chosen_account['scoreboard_color1'],chosen_account['scoreboard_color2'], chosen_account['scoreboard_text_color'], "False","", player_logo)
        insert_stmt = (
        "INSERT INTO player_accounts(discord_id, default_profile, header_color, background_color, scoreboard_color1, scoreboard_color2, scoreboard_text_color, verified, verified_name, player_logo)"
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            )
        print(data)
        mycursor = mydb.cursor()
        mycursor.execute(insert_stmt, data)
        mydb.commit()
    else:
        mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
            )
        sql = "UPDATE player_accounts SET player_logo = %s WHERE discord_id = %s"
        val = (player_logo, session['discord_id'])
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        mydb.commit()
        mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
            )
        sql = "UPDATE player_info SET player_logo = %s WHERE player_name = %s"
        val = (player_logo, player_settings[8])
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        mydb.commit()
    print(session['discord_id'])
    session['logged_in'] = True
    if '978549544340041728' in response.json()['roles']:
        session['no-ads'] = True
    return redirect("https://www.nw-stats.com/")

@app.route("/profile")
def profile():
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    # loop through the rows
    mycursor.execute("SELECT * FROM player_accounts")
    myresult = mycursor.fetchall()
    player_gear = ''
    role = "All"
    selected_player = ""
    player_log = ""
    for row in myresult:

        if int(row[0]) == int(session['discord_id']):
            selected_player = str(row[1])
            player_gear = get_player_gear(selected_player.lower())

    return render_template("player_stats.html", info = sql_stuff.calc_stats(selected_player.lower(), get_player_settings()[9]), war_logs=sql_stuff.get_user_wars(selected_player,role, get_player_settings()[9]), role = "N/A", player = selected_player, player_info = get_player_entered_info(selected_player.lower()), logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
, vods = get_submitted_vods(selected_player, get_player_settings()[9]), server = get_player_settings()[9], servers_played = get_servers_played(selected_player.lower()), player_logo = get_player_logo(selected_player), player_gear = player_gear, servers = get_servers_played(selected_player), all_servers = get_all_servers_global())

@app.route("/settings", methods = ['POST', 'GET'])
def edit_settings():
    if request.method == 'GET':

        return render_template('settings.html', message = "", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), server = "", all_servers = get_all_servers_global())
    if request.method == 'POST':
        print(request.form)
        form_data = request.form
        player = form_data
        setup_user_account(player)
        return render_template('settings.html', message = "Your information has been saved! Go to the profile page to view your stats easier!", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), server = "", all_servers = get_all_servers_global())

@app.route("/reset")
def reset_settings():
    reset_user_account([session['discord_id'],'none','#6b0bb9','#212224', '#6b0bb9', '#24023f','white',"COS"])
    return render_template('settings.html', message = "Your settings have been reset to default!", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), page = app.route, server="")

@app.route("/<server>/role/<role>")
def role_stats(role, server):
    return render_template("role_stats.html", content = "Testing", logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route, info = sql_stuff.get_role_stats(role, server), role = role, server = server)

@app.route("/<player>/editgear", methods = ['POST', 'GET'])
def gear_upload(player):
    found = False
    mydb = mysql.connector.connect(
                    host=config.db_host,
                    user=config.db_user,
                    password=config.db_pass,
                    database="superdotaplaya$war_stats"
                        )
    if request.method == 'GET':

        return render_template("gear_upload.html", content = "Testing", logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route, player = player, player_gear = get_player_gear(player)[:])
    if request.method == 'POST':

        if session['discord_id'] != '1' and get_player_settings()[8].lower() == player.lower():
            mycursor = mydb.cursor()
            sql = "SELECT * FROM player_gear WHERE player_name = %s"
            val = (player,)
            mycursor = mydb.cursor()
            mycursor.execute(sql,val)
            myresult = mycursor.fetchall()
            for item in myresult:
                if item[0] == player:
                    found = True
            if found == False:
                data = (f"{player}",)
                insert_stmt = (
                        "INSERT INTO player_gear(player_name)"
                        "VALUES (%s)"
                        )
                mycursor = mydb.cursor()
                mycursor.execute(insert_stmt,data)
                mydb.commit()
            form_data_images = request.files
            form_data_text = request.form
            slots = ['Head','Chest','Gloves','Pants','Boots','Amulet','Ring','Earring','Weapon_1', 'Weapon_2', 'Shield']
            for item in slots:
                if form_data_images[item]:
                    mydb = mysql.connector.connect(
                    host=config.db_host,
                    user=config.db_user,
                    password=config.db_pass,
                    database="superdotaplaya$war_stats"
                        )

                    file_name = form_data_images[item].filename[-3:]
                    if file_name != ".)>":
                        f = form_data_images[item]
                        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{player}_{item}.{file_name}"))
                        sql = f"UPDATE player_gear SET {item} = %s WHERE player_name = %s"
                        val = (f"/static/images/player_gear/{player}_{item}.{file_name}", player)
                        mycursor = mydb.cursor()
                        mycursor.execute(sql, val)
                        mydb.commit()


        return render_template("gear_upload.html", content = "Testing", logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route, player = player, player_gear = get_player_gear(player)[:])


@app.route("/news")
def news():
    return render_template('feedback_and_news.html', message = "", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), page = app.route, server = "")

@app.route("/submit_info", methods = ['POST', 'GET'])
def submit_info():
    user_settings = get_player_settings()
    player_name = user_settings[8]
    if request.method == "GET":
        return render_template('info_submission.html', message = "", logged_in = is_logged_in(), user_settings = user_settings, has_ads = has_ads(), page = app.route, server = "", player_info = get_player_entered_info(player_name))
    if request.method == 'POST':
        print(request.form)
        form_data = request.form
        mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
        )
        mycursor = mydb.cursor()
        sql = "SELECT * FROM player_info WHERE player_name = %s"
        val = (player_name,)
        mycursor.execute(sql,val)
        myresult = mycursor.fetchall()
        if len(myresult) == 0:
            sql = ("INSERT INTO player_info(player_name, player_company, player_role, faction, discord_name)"
            "VALUES (%s, %s, %s, %s, %s)")
            val = (player_name, form_data['company_name'],form_data['role'],form_data['faction'], form_data['discord_name'])
            mycursor.execute(sql, val)
            mydb.commit()
            return render_template('info_submission.html', message = "", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), page = app.route, server = "", player_info = get_player_entered_info(player_name))

        else:
            mycursor = mydb.cursor()
            mycursor.execute(sql,val)
            myresult = mycursor.fetchall()
            sql = "UPDATE player_info SET player_company = %s, player_role = %s, faction = %s, discord_name = %s WHERE player_name = %s"
            val = (form_data['company_name'],form_data['role'],form_data['faction'], form_data['discord_name'], player_name)

            mycursor.execute(sql, val)
            mydb.commit()
            user_settings = get_player_settings()
            player_name = user_settings[8]
            return render_template('info_submission.html', message = "", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), page = app.route, server = "", player_info = get_player_entered_info(player_name))

@app.route("/notifications")
def notifications():
    return render_template('get_notifications.html', message = "", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), page = app.route, server = "")

@app.route("/")
def region_selection():
    return render_template('server_selection.html', message = "", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), page = app.route, server = "", regions = region_names, servers = get_all_servers("ALL"), total_wars = get_total_wars_global())

@app.route("/<region>/server")
def server_selection(region):
    region = region.replace("%20"," ")
    return render_template('server_selection.html', message = "", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), page = app.route, server = "", regions = region_names, servers = get_all_servers(f"'{region}'"), region = region)


@app.route("/remove_vod", methods = ['POST', 'GET'])
def remove_vod_page():

    if request.method == "GET":
        return redirect("https://www.nw-stats.com")
    if request.method == 'POST':
        form_data = request.form
        removed_vod = form_data['vod']
        player = form_data['player']
        server = form_data['server']
        remove_vod(removed_vod,player,server)
        return redirect(f"https://www.nw-stats.com/{server}/player/{player}")


@app.route("/submit_war", methods = ['POST', 'GET'])
def submit_war_page():

    if request.method == "GET":
        return render_template('war_submission.html', message = "", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), page = app.route, server = "", all_servers = get_all_servers_global(), territories = territory_list)

    if request.method == 'POST':
       form_data_images = request.files
       form_data_text = request.form
       url = config.disc_hook
       f = form_data_images['scoreboard']
       filename = secure_filename(f.filename)
       f.save(os.path.join("mysite/assets/images/", filename))
       image_url = app.config['UPLOAD_FOLDER']+filename
       print(image_url)
       data = {
              "embeds": [{
                "fields": [
                  {
                    "name": "Server Name",
                    "value": f"{form_data_text['server']}"
                  },
                  {
                    "name": "War Date",
                    "value": f"{str(form_data_text['war_date'])}",
                    "inline": True
                  },
                  {
                    "name": "Territory",
                    "value": f"{str(form_data_text['territory'])}",
                    "inline": True
                  },
                  {
                    "name": "Winning Team",
                    "value": f"{form_data_text['war_winner']}",
                    "inline": False
                  },
                  {
                    "name": "Attacking Team Name",
                    "value": f"{form_data_text['attacker_name']}",
                    "inline": False
                  },
                  {
                    "name": "Attacking Team Faction",
                    "value": f"{form_data_text['attacker_faction']}",
                    "inline": False
                  },
                  {
                    "name": "Defending Team Name",
                    "value": f"{form_data_text['defender_name']}",
                    "inline": False
                  },
                  {
                    "name": "Defending Team Faction",
                    "value": f"{form_data_text['defender_faction']}",
                    "inline": False
                  },
                  {
                    "name": "War Stats",
                    "value": f"https://www.nw-stats.com/images/{filename}",
                    "inline": False
                  },
                ]
              }]

       }


       result = requests.post(url, json=data)
       if 200 <= result.status_code < 300:
           print(f"Webhook sent {result.status_code}")
       else:
           print(f"Not sent with {result.status_code}, response:\n{result.json()}")
       return render_template('war_submission.html', message = "", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), page = app.route, server = "", all_servers = get_all_servers_global(), territories = sorted(territory_list))

@app.route("/companion")
def companion_app():
        return render_template('companion_download_page.html', message = "", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), page = app.route, server = "")



@app.route("/<server>/leaderboards/<category>")
def get_server_leaderboards(server,category):
    leaderboards = get_leaderboards(category,server)
    print(leaderboards[:10])
    return render_template('leaderboards.html', message = "", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), page = app.route, server = server, leaderboard = leaderboards[:], category = category)

@app.route("/logout")
def offlog():
    session['logged_in'] = False
    session['discord_token'] = ""
    session['discord_id'] = ""
    session['no-ads'] = False
    return redirect("https://www.nw-stats.com")

@app.errorhandler(500)
def not_found(e):

# defining function
  return render_template("404.html", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), server = "", message = "We have run into a Grav Well & Ice Wall, Please try again or message SuperDotaPlaya#2014 if you beleive something is wrong!")

if __name__ == "__main__":
    app.run(debug=False)
