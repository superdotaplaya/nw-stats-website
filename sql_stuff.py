import mysql.connector
from mysql.connector import Error
import pygsheets
import config
import math
import mysql.connector
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import mpld3
from mpld3 import plugins

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
    myresult = mycursor.fetchall()
    attacks = []
    defenses = []
    misc = []
    for row in myresult:
        if role == "All":
            if row[2].lower() == requested_player.lower() and row[13] == "Attack":
                attacks.append(row)
            elif row[2].lower() == requested_player.lower() and row[13] == "Defense":
                defenses.append(row)
            elif row[2].lower() == requested_player.lower() and row[13] == "N/A":
                misc.append(row)

        else:
            if row[2].lower() == requested_player.lower() and row[13] == "Attack" and role.lower() == row[15].lower():
                attacks.append(row)
            elif row[2].lower() == requested_player.lower() and row[13] == "Defense" and role.lower() == row[15].lower():
                defenses.append(row)
            elif row[2].lower() == requested_player.lower() and row[13] == "N/A" and role.lower() == row[15].lower():
                misc.append(row)
    attacks.sort(key = lambda x: int(x[9].replace("*","").replace("^","")), reverse = True)
    defenses.sort(key = lambda x: int(x[9].replace("*","").replace("^","")), reverse = True)
    misc.sort(key = lambda x: int(x[9].replace("*","").replace("^","")), reverse = True)

    return(attacks[:],defenses[:],misc[:])

def get_user_wars_role(usr,role,server):
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
    val =(requested_player, server.lower())
    mycursor.execute(sql,val)
    myresult = mycursor.fetchall()
    attacks = []
    defenses = []
    misc = []
    if role == "All":
        for row in myresult:
            if row[2].lower() == requested_player.lower() and row[13] == "Attack":
                attacks.append(row)
            elif row[2].lower() == requested_player.lower() and row[13] == "Defense":
                defenses.append(row)
            elif row[2].lower() == requested_player.lower() and row[13] == "N/A":
                misc.append(row)
    else:
        for row in myresult:
            if row[2].lower() == requested_player.lower() and row[13] == "Attack" and row[15].lower() == role.lower() and row[16].lower() == server.lower():
                attacks.append(row)
            elif row[2].lower() == requested_player.lower() and row[13] == "Defense" and row[15].lower() == role.lower() and row[16].lower() == server.lower():
                defenses.append(row)
            elif row[2].lower() == requested_player.lower() and row[13] == "N/A" and row[15].lower() == role.lower() and row[16].lower() == server.lower():
                misc.append(row)
    attacks.reverse()
    defenses.reverse()
    misc.reverse()
    return(attacks[:],defenses[:],misc[:])

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

            x_axis = range(1,len(player_healing)+1)
            x = wars_played_in[:]
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

            ax.set_xlabel('War ID Number')
            ax.set_ylabel('Healing Amount')
            ax.set_title('Healing Performance', size=20)
            plt.figure(figsize=(3,2))

            for i, box in enumerate(boxes.get_children()):
                tooltip = mpld3.plugins.LineLabelTooltip(box, label=f"{y[i]} Healing")
                mpld3.plugins.connect(fig, tooltip)
            plugins.connect(fig, tooltip)

            return(mpld3.fig_to_html(fig))


        def get_damage_graph(player_damage, wars_played_in):

            x_axis = range(1,len(player_damage)+1)
            x = wars_played_in[:]
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

            ax.set_xlabel('War ID Number')
            ax.set_ylabel('Damage Amount')
            ax.set_title('Damage Performance', size=20)

            for i, box in enumerate(boxes.get_children()):
                tooltip = mpld3.plugins.LineLabelTooltip(box, label=f"{y[i]} Damage")
                mpld3.plugins.connect(fig, tooltip)
            plugins.connect(fig, tooltip)

            return(mpld3.fig_to_html(fig))

        player_stats = ["{:.2f}".format(avg_score),"{:.2f}".format(avg_kills),"{:.2f}".format(avg_deaths),"{:.2f}".format(avg_assists),"{:.2f}".format(avg_healing),"{:.2f}".format(avg_damage), "{:.2f}".format(healing_per_death), "{:.2f}".format(damage_per_death), max_kills, max_healing, max_damage, "{:.2f}".format(assists_per_death), total_kills, total_deaths, total_assists, total_damage, total_healing, "{:.2f}".format(kills_plus_assists_per_death),"{:.2f}".format(kills_per_death),get_healing_graph(player_healing, wars_played_in),get_damage_graph(player_damage, wars_played_in),max_healing_war,max_kill_war,max_assists_war,max_damage_war, max_assists, total_wins, total_losses, "{:.2f}".format(average_kpar), roles_played]

        return(player_stats)
    else:
        return([0,0,0,0,0,0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0, 0, 0, 0, 0, []])






def get_role_stats(role, server):
    player_results = []
    player_score = []
    player_kills = []
    player_deaths = []
    player_assists = []
    player_healing = []
    player_damage = []
    gc = pygsheets.authorize(service_file='credentials.json')
    sh = gc.open('blacktunastats.com player responses')
    wks = sh.worksheet_by_title("Form Responses 1")
    returned_values = wks.get_values_batch( ['A1:E500'] )
    role_players = []
    for player in returned_values[0]:
        if player[3].lower() == role.lower():
            role_players.append(player[1].lower())

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
        if row[15].lower() == role.lower() and "*" not in row[3] and row[16].lower() == server.lower():
            player_results.append(row)

            for player_entry in player_results:

                if "*" not in player_entry[3]:
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

            avg_score = sum(player_score)/len(player_score)
            avg_kills = sum(player_kills)/len(player_kills)
            avg_deaths = sum(player_deaths)/len(player_deaths)
            avg_assists = sum(player_assists)/len(player_assists)
            avg_healing = sum(player_healing)/len(player_healing)
            avg_damage = sum(player_damage)/len(player_damage)
            healing_per_death = sum(player_healing)/sum(player_deaths)
            damage_per_death = sum(player_damage)/sum(player_deaths)
            assists_per_death = sum(player_assists)/sum(player_deaths)
            kills_per_death = sum(player_kills)/sum(player_deaths)
            max_kills = max(player_kills)
            max_healing = max(player_healing)
            max_damage = max(player_damage)
            total_healing = sum(player_healing)
            total_assists = sum(player_assists)
            total_damage = sum(player_damage)
            total_deaths = sum(player_deaths)
            total_kills = sum(player_kills)
            kills_plus_assists_per_death = (sum(player_kills)+sum(player_assists))/sum(player_deaths)

            player_stats = ["{:.2f}".format(avg_score),"{:.2f}".format(avg_kills),"{:.2f}".format(avg_deaths),"{:.2f}".format(avg_assists),"{:.2f}".format(avg_healing),"{:.2f}".format(avg_damage), "{:.2f}".format(healing_per_death), "{:.2f}".format(damage_per_death), max_kills, max_healing, max_damage, "{:.2f}".format(assists_per_death), total_kills, total_deaths, total_assists, total_damage, total_healing, "{:.2f}".format(kills_plus_assists_per_death),"{:.2f}".format(kills_per_death)]
            mycursor.close()
            return(player_stats)




def create_table():
    mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
        )

    mycursor = mydb.cursor()
    sql = "DROP TABLE player_info"

    mycursor.execute(sql)
    add_table = """CREATE TABLE player_info (
                player_name VARCHAR(255),
                faction VARCHAR(255),
                player_role VARCHAR(255),
                player_company VARCHAR(255),
                player_logo VARCHAR(255)
                       )"""

    mycursor.execute(add_table)
    mydb.commit()


def setup_user_accounts():
    gc = pygsheets.authorize(service_file='credentials.json')

    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    sh = gc.open('blacktunastats.com player responses')
    wks = sh.worksheet_by_title("Form Responses 1")
    returned_values = wks.get_values_batch( ['A2:E500'] )
    for player_entry in returned_values[0]:
        data = (player_entry[1],player_entry[2],player_entry[3],player_entry[4])
        insert_stmt = (
        "INSERT INTO player_info(player_name,faction,player_role,player_company)"
        "VALUES (%s, %s, %s, %s)"
        )
        print(data)
        mycursor.execute(insert_stmt, data)
        mydb.commit()

