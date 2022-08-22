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
    val = (war_id.lower(),server.upper())
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
            return([war_stats],get_damage_graph(total_attacker_damage, total_defender_damage), get_healing_graph(total_attacker_healing, total_defender_healing), war_winner, total_attacker_damage, total_defender_damage, total_attacker_healing, total_defender_healing, total_attacker_kills, total_defender_kills, total_attacker_deaths, total_defender_deaths, total_attacker_assists, total_defender_assists, attacker_dmg_per_kill, defender_dmg_per_kill)
        if str(sort_by) == 'role':
            try:
                war_stats.sort(key = lambda x: x[15], reverse = True)
                return([war_stats], "","")
            except ValueError:
                return([war_stats], "","")
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
def search_war_results(searched_term):
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
    war_results = []
    wars = []
    for row in myresult:
        if searched_term.lower() in row[0].lower() and row[0] not in wars:
            war_results.append([row[0], row[9], row[16]])
            wars.append(row[0])
    return(war_results)

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
    mycursor.execute("SELECT * FROM player_records")
    myresult = mycursor.fetchall()
    player_results = []
    players = []
    for row in myresult:
        if searched_term.lower() in row[2].lower() and row[2] not in players:
            player_results.append([row[2],f"https://www.nw-stats.com/{row[16].lower()}/player/{row[2]}"])
            players.append(row[2])
    return(player_results)

def search_company_results(searched_term):
    sh = gc.open('blacktunastats.com player responses')
    wks = sh.worksheet_by_title("Form Responses 1")
    returned_values = wks.get_values_batch( ['A2:E1000'] )
    company_results = []
    companies = []
    for item in returned_values[0]:
        if searched_term.lower() in item[4].lower() and item[4] not in companies:
            company_results.append([item[4], f"https://www.nw-stats.com/company/{item[4]}"])
            companies.append(item[4])
    return(company_results)

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
        if row[11] != "N/A" and row[16].lower() == server:
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

def get_war_list(page, server):
    war_list = []
    if server == "cos":
        sh = gc.open('Testing war dumps')
    elif server == "ygg":
        sh = gc.open('YGG war records')
    elif server == "del":
        sh = gc.open('Delos war records')
    elif server == "val":
        sh = gc.open('Valhalla war records')
    elif server == "oro":
        sh = gc.open('Orofena war records')
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



def get_total_wars(page, server):

    pages_list = []
    if server == "cos":
        sh = gc.open('Testing war dumps')
    elif server == "ygg":
        sh = gc.open('YGG war records')
    elif server == "del":
        sh = gc.open('Delos war records')
    elif server == "val":
        sh = gc.open('Valhalla war records')
    elif server == "oro":
        sh = gc.open('Orofena war records')
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

def get_total_wars_global():
    total_wars = 0
    sh = gc.open('Testing war dumps')
    wks = sh.worksheet_by_title("War List")
    returned_values = wks.get_values_batch( ['A1:C1000'] )
    total_wars += len(returned_values[0])
    sh = gc.open('YGG war records')
    wks = sh.worksheet_by_title("War List")
    returned_values = wks.get_values_batch( ['A1:C1000'] )
    total_wars += len(returned_values[0])
    sh = gc.open('Delos war records')
    wks = sh.worksheet_by_title("War List")
    sh = gc.open('Valhalla war records')
    wks = sh.worksheet_by_title("War List")
    sh = gc.open('Orofena war records')
    wks = sh.worksheet_by_title("War List")
    returned_values = wks.get_values_batch( ['A1:C1000'] )
    total_wars += len(returned_values[0])
    return(total_wars)


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
    if server == "cos":
        sh = gc.open('Testing war dumps')
    elif server == "ygg":
        sh = gc.open('YGG war records')
    elif server == "del":
        sh = gc.open('Delos war records')
    elif server == "val":
        sh = gc.open('Valhalla war records')
    elif server == "oro":
        sh = gc.open('Orofena war records')
    wks = sh.worksheet_by_title("War List")
    returned_values = wks.get_values_batch( ['A1:F1000'] )
    for item in returned_values[0]:
        if str(item[0]) == str(war_id):
            return([item[1],item[2],item[4],item[5],item[3]])

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

    player_stats = ["{:.2f}".format(avg_score),"{:.2f}".format(avg_kills),"{:.2f}".format(avg_deaths),"{:.2f}".format(avg_assists),"{:.2f}".format(avg_healing),"{:.2f}".format(avg_damage), "{:.2f}".format(healing_per_death), "{:.2f}".format(damage_per_death), max_kills, max_healing, max_damage, "{:.2f}".format(assists_per_death), total_kills, total_deaths, total_assists, total_damage, total_healing, "{:.2f}".format(kills_plus_assists_per_death),"{:.2f}".format(kills_per_death),get_healing_graph(player_healing),get_damage_graph(player_damage),max_healing_war,max_kill_war,max_assists_war,max_damage_war, max_assists, total_wins, total_losses, "{:.2f}".format(average_kpar), roles_played]

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
    mycursor.execute("SELECT * FROM player_records")
    myresult = mycursor.fetchall()
    servers_played = []
    for item in myresult:
        if item[16].lower() not in servers_played and item[2].lower() == player.lower():
            servers_played.append(item[16].lower())
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



@app.route("/<server>/war/<war_id>", methods=["POST", "GET"])
def war(server, war_id):
    if request.method == "POST":
        war_requested = request.form["war"]
        return render_template("war.html",info = get_war_stats(war_requested,'none', server)[:], war_title = get_war_title(war_requested, server), player_links = get_user_links(war_requested), logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
    , war_id = war_id, vods = get_submitted_vods(war_id, server), server = server)
    else:
        return render_template("war.html", info= get_war_stats(war_id, 'none', server)[:], war_title = get_war_title(war_id, server), war_link = war_id, sorted_by = "none", logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
    , war_id = war_id, vods = get_submitted_vods(war_id, server), server = server)

@app.route("/<server>/war/<war_id>/<sort_by>", methods=["POST", "GET"])
def war_sorted(server, war_id,sort_by):
    return render_template("war.html", info= get_war_stats(war_id,str(sort_by), server), war_title = get_war_title(war_id, server), player_links = get_user_links(war_id), war_link = war_id, sorted_by = sort_by, logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
, vods = get_submitted_vods(war_id, server), server = server)

@app.route("/<server>/compare/role/<role>/<usr>", methods=["POST", "GET"])
def compare_stats(role,usr, server):
        return render_template("player_vs_role.html", info= get_player_role_stats(usr,role,server), war_logs=sql_stuff.get_user_wars(usr, role, server), role = role, player = usr, player_info = get_player_info(usr), logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
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
    return render_template("player_stats.html", info= sql_stuff.calc_stats(usr,server), war_logs=sql_stuff.get_user_wars(usr, role, server), role = role, player = usr, player_info = get_player_info(usr), logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
, vods = get_submitted_vods(player, server), server = server, servers_played = servers_played)

@app.route("/<server>/player/<usr>/<player_role>")
def user_role_stats(usr,player_role, server):
    print(usr)
    print(player_role)
    info = get_player_role_stats(usr,player_role, server)
    servers_played = get_servers_played(usr)
    return render_template("player_stats.html", info= info, war_logs=sql_stuff.get_user_wars_role(usr,player_role, server), player = usr, role = player_role, player_info = get_player_info(usr), logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
, vods = get_submitted_vods(usr, server), server = server, servers_played = servers_played)


@app.route("/<server>/update_role/<usr>/<war_id>", methods = ['POST', 'GET'])
def enter_role(server,usr,war_id):
    if request.method == "POST":
        role = request.form['role_played']
        message = set_war_role(usr,war_id,role,server)

        return render_template("enter_role_info.html", player = usr, logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
    , selected_war = get_selected_war(war_id, usr), war_id = war_id, message = message, server = server)
    else:
        return render_template("enter_role_info.html", player = usr, logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
    , selected_war = get_selected_war(war_id, usr), war_id = war_id, message = "", server = server)

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


@app.route("/<server>/player/<usr>/wars")
def user_wars(usr, server):
    role = "All"
    return render_template("all_wars.html", info= sql_stuff.calc_stats(usr, server), war_logs=sql_stuff.get_user_wars(usr, role, server), player = usr, player_info = get_player_info(usr), logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
, war_vods = get_submitted_vods(usr, server), server = server)


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
        return render_template('search.html',form_data="", search_term = "", logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route, server = server
    )
    if request.method == 'POST':
        print(request.form)
        form_data = request.form
        search_term = form_data['searched_term']
        return(render_template('search.html',form_data = form_data, player_results = search_player_results(search_term), company_results = search_company_results(search_term), war_results= search_war_results(search_term), searched_term = search_term, logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route, server = server
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
        data = (session['discord_id'], chosen_account['player_name'], chosen_account['header_color'], chosen_account['background_color'], chosen_account['scoreboard_color1'],chosen_account['scoreboard_color2'], chosen_account['scoreboard_text_color'], "False","")
        insert_stmt = (
        "INSERT INTO player_accounts(discord_id, default_profile, header_color, background_color, scoreboard_color1, scoreboard_color2, scoreboard_text_color, verified, verified_name)"
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            )
        print(data)
        mycursor = mydb.cursor()
        mycursor.execute(insert_stmt, data)
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
    role = "All"
    selected_player = ""

    for row in myresult:

        if int(row[0]) == int(session['discord_id']):
            selected_player = str(row[1])
    return render_template("player_stats.html", info= sql_stuff.calc_stats(selected_player.lower(), get_player_settings()[9]), war_logs=sql_stuff.get_user_wars(selected_player,role, get_player_settings()[9]), role = "N/A", player = selected_player, player_info = get_player_info(selected_player), logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route
, vods = get_submitted_vods(selected_player, get_player_settings()[9]), server = get_player_settings()[9], servers_played = get_servers_played(selected_player.lower()))

@app.route("/settings", methods = ['POST', 'GET'])
def edit_settings():
    if request.method == 'GET':

        return render_template('settings.html', message = "", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), server = "")
    if request.method == 'POST':
        print(request.form)
        form_data = request.form
        player = form_data
        setup_user_account(player)
        return render_template('settings.html', message = "Your information has been saved! Go to the profile page to view your stats easier!", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), server = "")

@app.route("/reset")
def reset_settings():
    reset_user_account([session['discord_id'],'none','#6b0bb9','#212224', '#6b0bb9', '#24023f','white',"COS"])
    return render_template('settings.html', message = "Your settings have been reset to default!", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), page = app.route, server="")

@app.route("/<server>/role/<role>")
def role_stats(role, server):
    return render_template("role_stats.html", content = "Testing", logged_in = is_logged_in(), has_ads = has_ads(), user_settings = get_player_settings(), page = app.route, info = sql_stuff.get_role_stats(role, server), role = role, server = server)

@app.route("/news")
def news():
    return render_template('feedback_and_news.html', message = "", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), page = app.route, server = "")

@app.route("/notifications")
def notifications():
    return render_template('get_notifications.html', message = "", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), page = app.route, server = "")

@app.route("/")
def server_select():
    return render_template('server_selection.html', message = "", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), page = app.route, server = "")

# End discord login
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
  return render_template("404.html", logged_in = is_logged_in(), user_settings = get_player_settings(), has_ads = has_ads(), server = "")

if __name__ == "__main__":
    app.run(debug=True)
