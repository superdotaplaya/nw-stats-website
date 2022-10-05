import mysql.connector
from mysql.connector import Error
import pygsheets
import config
import math
from pusher_push_notifications import PushNotifications

beams_client = PushNotifications(
    instance_id=config.beam_instance,
    secret_key=config.beam_secret,
)

# Set to "Add" to add the latest war to the database, Set to "All, to reload the entire database, Set to war number to reload stats for that war, Set to "Repair" to remove duplicate wars.
updating = "Add"
server = "YGG"


gc = pygsheets.authorize(service_file='credentials.json')
def get_player_info():
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM player_info")
    returned_values = mycursor.fetchall()
    return(returned_values)



def update_stats(player_info):
    gc = pygsheets.authorize(service_file='credentials.json')
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    player_role = ""
    mycursor = mydb.cursor()
    mycursor.execute("TRUNCATE player_records")
    mydb.commit()
    if server == "COS":
        sh = gc.open('Testing war dumps')
    elif server == "YGG":
        sh = gc.open('YGG war records')
    elif server == "DEL":
        sh = gc.open('Delos war records')
    elif server == "VAL":
        sh = gc.open('Valhalla war records')
    elif server.lower() == "oro":
        sh = gc.open('Orofena war records')
    elif server.lower() == "mar":
        sh = gc.open('Maramma war records')
    elif server.lower() == "eri":
        sh = gc.open('Eridu war records')
    info = sh.worksheets()
    sheet_id = 1
    war_name = ""
    for sheet in info[1:]:
        sheet_title = sheet.title
        wks = sh.worksheet_by_title(str(sheet_title))
        returned_values = wks.get_values_batch( ['A1:J500'] )
        war_name_sheet = sh.worksheet_by_title("War List")
        returned_values_war_names = war_name_sheet.get_values_batch( ['A1:D500'] )

        war_link = ""
        attackers_kills = []
        defenders_kills = []
        k_par = 0
        dmg_kpar = 0
        war_winner = ""

        kills_list = []
        for war_item in returned_values_war_names[0]:
            if int(war_item[0]) == int(sheet_id):
                war_name = str(war_item[1])
                war_link = f"https://www.nw-stats.com/war/{war_item[0]}"
                war_id = war_item[0]
                try:
                    if war_item[3] == "Attack":
                        war_winner = "Attack"
                    elif war_item[3] == "Defense":
                        war_winner = "Defense"
                    else:
                        war_winner = "N/A"
                except:
                    war_winner = "N/A"
        for player in returned_values[0]:
            if player[8] == "Attack":
                attackers_kills.append(int(player[3].replace("*","")))
            if player[8] == "Defense":
                defenders_kills.append(int(player[3].replace("*","")))
            kills_list.append(int(player[3].replace("*","").replace("*","")))
        attacker_kills_total = sum(attackers_kills)
        defender_kills_total = sum(defenders_kills)
        for player in returned_values[0]:
            found = False
            player_rank = player[0]
            player_name = player[1]
            player_score = int(player[2].replace("*",""))
            player_kills = int(player[3].replace("*",""))
            player_deaths = int(player[4].replace("*",""))
            player_assists = int(player[5].replace("*",""))
            player_healing = int(player[6].replace("*",""))
            player_damage = int(player[7].replace("*",""))
            player_score_board = player[2]
            player_kills_board = player[3]
            player_deaths_board = player[4]
            player_assists_board = player[5]
            player_healing_board = player[6]
            player_damage_board = player[7]
            for item in player_info:
                if player_name.lower() == item[1].lower():
                    player_role = item[3]
                    found = True
            if found == False:
                player_role = "N/A"

            try:
                dmg_kpar = player_damage/(player_kills + player_assists)
            except:
                dmg_kpar = 0
            if player[8] == "Attack":
                k_par = (player_kills + player_assists) / attacker_kills_total
            if player[8] == "Defense":
                k_par = (player_kills + player_assists) / defender_kills_total
            if player[8] == "N/A" and len(returned_values[0]) < 100:
                k_par = (player_kills + player_assists) / sum(kills_list)
            elif player[8] == "N/A":
                k_par = "N/A"
            if k_par != "N/A":
                data = (war_name,player_rank,player_name,player_score_board,player_kills_board,player_deaths_board,player_assists_board,player_healing_board,player_damage_board, war_id, war_link, round(k_par*100,2), round(dmg_kpar,2), player[9], war_winner, player_role, server)
                insert_stmt = (
            "INSERT INTO player_records(war_name, war_rank, name, score, kills, deaths, assists, healing, damage, war_id, war_link, k_par, dmg_kpar, team, war_winner, player_role, server)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            )
                print(data)
                mycursor.execute(insert_stmt, data)
                mydb.commit()
            else:
                data = (war_name,player_rank,player_name,player_score_board,player_kills_board,player_deaths_board,player_assists_board,player_healing_board,player_damage_board, war_id, war_link, k_par, round(dmg_kpar,2), player[9], war_winner, player_role, server)
                insert_stmt = (
            "INSERT INTO player_records(war_name, war_rank, name, score, kills, deaths, assists, healing, damage, war_id, war_link, k_par, dmg_kpar, team, war_winner, player_role, server)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            )
                print(data)
                mycursor.execute(insert_stmt, data)
                mydb.commit()
        sheet_id += 1

def add_player_averages(player,server, war_stats):

    mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
        )
    mycursor = mydb.cursor()
    sql = "SELECT * FROM player_averages WHERE player_name = %s AND server = %s"
    val = (player, server)
    mycursor.execute(sql,val)
    myresult_current_averages = mycursor.fetchall()
    if len(myresult_current_averages) != 0 and '*' not in war_stats[0]:
        player_avg_score = int(float(myresult_current_averages[0][2]))
        player_avg_kills = int(float(myresult_current_averages[0][3]))
        player_avg_assists = int(float(myresult_current_averages[0][4]))
        player_avg_healing = int(float(myresult_current_averages[0][5]))
        player_avg_damage = int(float(myresult_current_averages[0][6]))
        total_wars = int(myresult_current_averages[0][7])+1
        new_avg_score = (player_avg_score + int(float(war_stats[0])))/total_wars
        new_avg_kills = (player_avg_kills + float(war_stats[1]))/total_wars
        new_avg_assists = (player_avg_assists + float(war_stats[2]))/total_wars
        new_avg_healing = (player_avg_healing + float(war_stats[3]))/total_wars
        new_avg_damage = (player_avg_damage + float(war_stats[4]))/total_wars
        sql = "UPDATE player_averages SET avg_score = %s, avg_kills = %s, avg_assists = %s, avg_healing = %s, avg_damage = %s, total_wars = %s"
        val = (new_avg_score,new_avg_kills,new_avg_assists,new_avg_healing,new_avg_damage, total_wars)
        print(val)
        mycursor.execute(sql,val)
        mydb.commit()
    elif len(myresult_current_averages) == 0 and '*' not in war_stats[0]:
        total_wars = 1
        player_avg_score = war_stats[0]
        player_avg_kills = war_stats[1]
        player_avg_assists = war_stats[2]
        player_avg_healing = war_stats[3]
        player_avg_damage = war_stats[4]
        data = (player, server, player_avg_score, player_avg_kills, player_avg_assists, player_avg_healing, player_avg_damage, total_wars)
        insert_stmt = (
        "INSERT INTO player_averages(player_name, server, avg_score, avg_kills, avg_assists, avg_healing, avg_damage, total_wars)"
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        print(f"Adding: {data}")
        mycursor = mydb.cursor()
        mycursor.execute(insert_stmt, data)
        mydb.commit()

def update_player_averages(player,server):
    mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
        )
    mycursor = mydb.cursor()
    total_wars = 0
    player_scores = []
    player_kills = []
    player_assists = []
    player_healing = []
    player_damage = []
    sql = "SELECT * FROM player_records WHERE name = %s AND server = %s"
    val = (player, server)
    mycursor.execute(sql,val)
    myresult = mycursor.fetchall()
    for row in myresult:
        if "*" not in row[3]:
            total_wars = total_wars + 1
            player_scores.append(int(row[3]))
            player_kills.append(int(row[4]))
            player_assists.append(int(row[6]))
            player_healing.append(int(row[7]))
            player_damage.append(int(row[8]))

    if len(player_scores) != 0:
        player_avg_score = sum(player_scores)/len(player_scores)
        player_avg_kills = sum(player_kills)/len(player_kills)
        player_avg_assists = sum(player_assists)/len(player_assists)
        player_avg_healing = sum(player_healing)/len(player_healing)
        player_avg_damage = sum(player_damage)/len(player_damage)

        sql = "UPDATE player_averages SET avg_score = %s, avg_kills = %s, avg_assists = %s, avg_healing = %s, avg_damage = %s, total_wars = %s WHERE player_name = %s AND server = %s"
        val = (player_avg_score,player_avg_kills,player_avg_assists,player_avg_healing,player_avg_damage, total_wars, player, server)
        print(f"Updating: {val}")

        mycursor.execute(sql, val)
        mydb.commit()

def add_war(server,war_num):
    try:
        gc = pygsheets.authorize(service_file='credentials.json')
        player_info = get_player_info()
        mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
        )
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
        mycursor = mydb.cursor()
        sh = gc.open(f'{server} war records')

        wks = sh.worksheet_by_title(str(war_num))
        returned_values = wks.get_values_batch( ['A1:J500'] )
        war_name_sheet = sh.worksheet_by_title("War List")
        returned_values_war_names = war_name_sheet.get_values_batch( ['A1:D500'] )
        war_name = ""
        war_link = ""
        attackers_kills = []
        defenders_kills = []
        k_par = 0
        dmg_kpar = 0
        war_winner = ""
        war_id = ""
        kills_list = []
        for war_item in returned_values_war_names[0]:
            if int(war_item[0]) == int(war_num):
                war_name = str(war_item[1])
                war_link = f"https://www.blacktunastats.com/war/{war_item[0]}"
                war_id = war_item[0]
                try:
                    if war_item[3] == "Attack":
                        war_winner = "Attack"
                    elif war_item[3] == "Defense":
                        war_winner = "Defense"
                    else:
                        war_winner = "N/A"
                except:
                    war_winner = "N/A"
        for player in returned_values[0]:
            if player[8] == "Attack":
                attackers_kills.append(int(player[3].replace("*","")))
            if player[8] == "Defense":
                defenders_kills.append(int(player[3].replace("*","")))
            kills_list.append(int(player[3].replace("*","").replace("*","")))
        attacker_kills_total = sum(attackers_kills)
        defender_kills_total = sum(defenders_kills)
        for player in returned_values[0]:
            found = False
            player_rank = player[0]
            player_name = player[1]
            player_score = int(player[2].replace("*",""))
            player_kills = int(player[3].replace("*",""))
            player_deaths = int(player[4].replace("*",""))
            player_assists = int(player[5].replace("*",""))
            player_healing = int(player[6].replace("*",""))
            player_damage = int(player[7].replace("*",""))
            player_score_board = player[2]
            player_kills_board = player[3]
            player_deaths_board = player[4]
            player_assists_board = player[5]
            player_healing_board = player[6]
            player_damage_board = player[7]
            for item in player_info:
                if player_name.lower() == item[0].lower():
                    player_role = item[2]
                    found = True
                if found == False:
                    player_role = "N/A"
            try:
                dmg_kpar = player_damage/(player_kills + player_assists)
            except:
                dmg_kpar = 0
            if player[8] == "Attack":
                k_par = (player_kills + player_assists) / attacker_kills_total
            if player[8] == "Defense":
                k_par = (player_kills + player_assists) / defender_kills_total
            if player[8] == "N/A" and len(returned_values[0]) < 100:
                k_par = (player_kills + player_assists) / sum(kills_list)
            elif player[8] == "N/A":
                k_par = "N/A"
            if k_par != "N/A":
                data = (war_name,player_rank,player_name,player_score_board,player_kills_board,player_deaths_board,player_assists_board,player_healing_board,player_damage_board, war_id, war_link, round(k_par*100,2), round(dmg_kpar,2), player[9], war_winner, player_role, server)
                insert_stmt = (
            "INSERT INTO player_records(war_name, war_rank, name, score, kills, deaths, assists, healing, damage, war_id, war_link, k_par, dmg_kpar, team, war_winner, player_role, server)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            )
                print(data)
                mycursor.execute(insert_stmt, data)
                mydb.commit()
                update_player_averages(player_name,server)
            else:
                data = (war_name,player_rank,player_name,player_score_board,player_kills_board,player_deaths_board,player_assists_board,player_healing_board,player_damage_board, war_id, war_link, k_par, round(dmg_kpar,2), player[9], war_winner, player_role, server)
                insert_stmt = (
            "INSERT INTO player_records(war_name, war_rank, name, score, kills, deaths, assists, healing, damage, war_id, war_link, k_par, dmg_kpar, team, war_winner, player_role, server)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            )
                print(data)
                mycursor.execute(insert_stmt, data)
                mydb.commit()
                update_player_averages(player_name,server)

        response = beams_client.publish_to_interests(
          interests=['hello'],
          publish_body={
            'web': {
              'notification': {
                'title': 'New War Entered on NW- Stats!',
                'body': f"{war_name}",
                'deep_link': f"https://www.nw-stats.com/{server}/war/{war_id}",
              },
            },
          },
        )

        print(response['publishId'])
        return(f"Stats for this war are now live at: https://www.nw-stats.com/{server}/war/{war_id}")
    except:
        return("Could not add stats to the site, check the spreadsheet and the websites war page before trying again.")

def add_invasion(server,invasion_num):
    try:
        gc = pygsheets.authorize(service_file='credentials.json')
        player_info = get_player_info()
        mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
        )
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
        mycursor = mydb.cursor()
        sh = gc.open(f'{server} invasion records')

        wks = sh.worksheet_by_title(str(invasion_num))
        returned_values = wks.get_values_batch( ['A1:J500'] )
        war_name_sheet = sh.worksheet_by_title("Invasion List")
        returned_values_war_names = war_name_sheet.get_values_batch( ['A1:D500'] )
        invasion_name = ""
        attackers_kills = []
        defenders_kills = []
        k_par = 0
        dmg_kpar = 0
        invasion_winner = ""
        invasion_id = ""
        kills_list = []
        for invasion_item in returned_values_war_names[0]:
            if int(invasion_item[0]) == int(invasion_num):
                invasion_name = str(invasion_item[1])
                invasion_id = invasion_item[0]
                try:
                    if invasion_item[3] == "Attack":
                        invasion_winner = "Attack"
                    elif invasion_item[3] == "Defense":
                        invasion_winner = "Defense"
                    else:
                        invasion_winner = "N/A"
                except:
                    invasion_winner = "N/A"
        for player in returned_values[0]:
            if player[8] == "Attack":
                attackers_kills.append(int(player[3].replace("*","")))
            if player[8] == "Defense":
                defenders_kills.append(int(player[3].replace("*","")))
            kills_list.append(int(player[3].replace("*","").replace("*","")))
        attacker_kills_total = sum(attackers_kills)
        defender_kills_total = sum(defenders_kills)
        for player in returned_values[0]:
            found = False
            player_rank = player[0]
            player_name = player[1]
            player_score = int(player[2].replace("*",""))
            player_kills = int(player[3].replace("*",""))
            player_deaths = int(player[4].replace("*",""))
            player_assists = int(player[5].replace("*",""))
            player_healing = int(player[6].replace("*",""))
            player_damage = int(player[7].replace("*",""))
            player_score_board = player[2]
            player_kills_board = player[3]
            player_deaths_board = player[4]
            player_assists_board = player[5]
            player_healing_board = player[6]
            player_damage_board = player[7]
            for item in player_info:
                if player_name.lower() == item[0].lower():
                    player_role = item[2]
                    found = True
                if found == False:
                    player_role = "N/A"
            try:
                dmg_kpar = player_damage/(player_kills + player_assists)
            except:
                dmg_kpar = 0
            if player[8] == "Attack":
                k_par = (player_kills + player_assists) / attacker_kills_total
            if player[8] == "Defense":
                k_par = (player_kills + player_assists) / defender_kills_total
            if player[8] == "N/A" and len(returned_values[0]) < 100:
                k_par = (player_kills + player_assists) / sum(kills_list)
            elif player[8] == "N/A":
                k_par = "N/A"
            if k_par != "N/A":
                data = (invasion_name,player_rank,player_name,player_score_board,player_kills_board,player_deaths_board,player_assists_board,player_healing_board,player_damage_board, invasion_id, invasion_winner, server)
                insert_stmt = (
                "INSERT INTO invasion_records(invasion_name, rank, name, score, kills, deaths, assists, healing, damage, invasion_id, invasion_winner, server)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                )
                print(data)
                mycursor.execute(insert_stmt, data)
                mydb.commit()
            else:
                data = (invasion_name,player_rank,player_name,player_score_board,player_kills_board,player_deaths_board,player_assists_board,player_healing_board,player_damage_board, invasion_id, invasion_winner, server)
                insert_stmt = (
            "INSERT INTO invasion_records(invasion_name, rank, name, score, kills, deaths, assists, healing, damage, invasion_id, invasion_winner, server)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            )
                print(data)
                mycursor.execute(insert_stmt, data)
                mydb.commit()

        return(f"Stats for this invasion are now live at: https://www.nw-stats.com/{server}/invasion/{invasion_id}")
    except:
        return("Could not add stats to the site, check the spreadsheet and the websites invasion page before trying again.")

def fix_stats(server,updating_war):
    try:
        gc = pygsheets.authorize(service_file='credentials.json')
        player_info = get_player_info()
        mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
        )

        mycursor = mydb.cursor()

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
        sh = gc.open(f'{server} invasion records')
        wks = sh.worksheet_by_title(str(updating_war))
        returned_values = wks.get_values_batch( ['A1:J500'] )
        war_name_sheet = sh.worksheet_by_title("War List")
        returned_values_war_names = war_name_sheet.get_values_batch( ['A1:D500'] )
        war_name = ""
        war_link = ""
        attackers_kills = []
        defenders_kills = []
        k_par = 0
        dmg_kpar = 0
        war_winner = ""
        war_name = ""
        for war_number in returned_values_war_names[0]:
            if int(war_number[0]) == int(updating_war):
                war_name = war_number[1]


        kills_list = []
        for war_item in returned_values_war_names[0]:
            if war_item[0] == updating_war:
                war_winner = war_item[3]
        for player in returned_values[0]:
            if player[8] == "Attack":
                attackers_kills.append(int(player[3].replace("*","")))
            if player[8] == "Defense":
                defenders_kills.append(int(player[3].replace("*","")))
            kills_list.append(int(player[3].replace("*","").replace("*","")))
        attacker_kills_total = sum(attackers_kills)
        defender_kills_total = sum(defenders_kills)
        for player in returned_values[0]:
            found = False
            player_rank = player[0]
            player_name = player[1]
            player_score = int(player[2].replace("*",""))
            player_kills = int(player[3].replace("*",""))
            player_deaths = int(player[4].replace("*",""))
            player_assists = int(player[5].replace("*",""))
            player_healing = int(player[6].replace("*",""))
            player_damage = int(player[7].replace("*",""))
            player_score_board = player[2]
            player_kills_board = player[3]
            player_deaths_board = player[4]
            player_assists_board = player[5]
            player_healing_board = player[6]
            player_damage_board = player[7]
            for item in player_info:
                if player_name.lower() == item[1].lower():
                    player_role = item[3]
                    found = True
                if found == False:
                    player_role = "N/A"
            try:
                dmg_kpar = player_damage/(player_kills + player_assists)
            except:
                dmg_kpar = 0
            if player[8] == "Attack":
                k_par = (player_kills + player_assists) / attacker_kills_total
            if player[8] == "Defense":
                k_par = (player_kills + player_assists) / defender_kills_total
            if player[8] == "N/A" and len(returned_values[0]) < 100:
                k_par = (player_kills + player_assists) / sum(kills_list)
            elif player[8] == "N/A":
                k_par = "N/A"
            if k_par != "N/A":

                sql = "UPDATE player_records SET war_name = %s, war_rank = %s, name = %s, score = %s, kills = %s, deaths = %s, assists = %s, healing = %s, damage = %s, k_par = %s, dmg_kpar = %s, team = %s, war_winner = %s WHERE war_id = %s AND war_rank = %s AND server = %s"
                val = (war_name,player_rank,player_name,player_score_board,player_kills_board,player_deaths_board,player_assists_board,player_healing_board,player_damage_board, round(k_par*100,2), round(dmg_kpar,2), player[9], war_winner, updating_war,player_rank, server)
                print(val)
                mycursor.execute(sql,val)
                mydb.commit()
                update_player_averages(player_name,server)
            else:
                sql = "UPDATE player_records SET war_name = %s, war_rank = %s, name = %s, score = %s, kills = %s, deaths = %s, assists = %s, healing = %s, damage = %s, dmg_kpar = %s, team = %s, war_winner = %s WHERE war_id = %s AND war_rank = %s AND server = %s"
                val = (war_name,player_rank,player_name,player_score_board,player_kills_board,player_deaths_board,player_assists_board,player_healing_board,player_damage_board, "N/A", round(dmg_kpar,2), player[9], war_winner, updating_war,player_rank, server)
                mycursor.execute(sql,val)
                print(val)
                update_player_averages(player_name,server)
                mydb.commit()

        return(f"Stats have been updated for this war, ensure the changes are on the website here: https://www.nw-stats.com/{server}/war/{updating_war}")
    except:
        return(f"There was an error when trying to fix the stats for war {updating_war}, Please use the /deletewar command to remove it from the site, correct any errors on the spreadsheet, then run the /enterstats command to add the war back to the website!")

def fix_invasion_stats(server,updating_invasion):
    try:
        gc = pygsheets.authorize(service_file='credentials.json')
        player_info = get_player_info()
        mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
        )

        mycursor = mydb.cursor()

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
        sh = gc.open(f'{server} invasion records')
        wks = sh.worksheet_by_title(str(updating_invasion))
        returned_values = wks.get_values_batch( ['A1:J500'] )
        war_name_sheet = sh.worksheet_by_title("Invasion List")
        returned_values_invasion_names = war_name_sheet.get_values_batch( ['A1:D500'] )
        invasion_name = ""
        attackers_kills = []
        defenders_kills = []
        k_par = 0
        dmg_kpar = 0
        invasion_winner = ""
        invasion_name = ""
        for invasion_number in returned_values_invasion_names[0]:
            if int(invasion_number[0]) == int(updating_invasion):
                invasion_name = invasion_number[1]


        kills_list = []
        for invasion_item in returned_values_invasion_names[0]:
            if invasion_item[0] == updating_invasion:
                invasion_winner = invasion_item[3]
        for player in returned_values[0]:
            if player[8] == "Attack":
                attackers_kills.append(int(player[3].replace("*","")))
            if player[8] == "Defense":
                defenders_kills.append(int(player[3].replace("*","")))
            kills_list.append(int(player[3].replace("*","").replace("*","")))
        attacker_kills_total = sum(attackers_kills)
        defender_kills_total = sum(defenders_kills)
        for player in returned_values[0]:
            found = False
            player_rank = player[0]
            player_name = player[1]
            player_score = int(player[2].replace("*",""))
            player_kills = int(player[3].replace("*",""))
            player_deaths = int(player[4].replace("*",""))
            player_assists = int(player[5].replace("*",""))
            player_healing = int(player[6].replace("*",""))
            player_damage = int(player[7].replace("*",""))
            player_score_board = player[2]
            player_kills_board = player[3]
            player_deaths_board = player[4]
            player_assists_board = player[5]
            player_healing_board = player[6]
            player_damage_board = player[7]
            for item in player_info:
                if player_name.lower() == item[1].lower():
                    player_role = item[3]
                    found = True
                if found == False:
                    player_role = "N/A"
            try:
                dmg_kpar = player_damage/(player_kills + player_assists)
            except:
                dmg_kpar = 0
            if player[8] == "Attack":
                k_par = (player_kills + player_assists) / attacker_kills_total
            if player[8] == "Defense":
                k_par = (player_kills + player_assists) / defender_kills_total
            if player[8] == "N/A" and len(returned_values[0]) < 100:
                k_par = (player_kills + player_assists) / sum(kills_list)
            elif player[8] == "N/A":
                k_par = "N/A"
            if k_par != "N/A":

                sql = "UPDATE invasion_records SET invasion_name = %s, rank = %s, name = %s, score = %s, kills = %s, deaths = %s, assists = %s, healing = %s, damage = %s, invasion_winner = %s WHERE invasion_id = %s AND rank = %s AND server = %s"
                val = (invasion_name,player_rank,player_name,player_score_board,player_kills_board,player_deaths_board,player_assists_board,player_healing_board,player_damage_board, invasion_winner, updating_invasion,player_rank, server)
                print(val)
                mycursor.execute(sql,val)
                mydb.commit()
            else:
                sql = "UPDATE invasion_records SET invasion_name = %s, rank = %s, name = %s, score = %s, kills = %s, deaths = %s, assists = %s, healing = %s, damage = %s, invasion_winner = %s WHERE invasion_id = %s AND rank = %s AND server = %s"
                val = (invasion_name,player_rank,player_name,player_score_board,player_kills_board,player_deaths_board,player_assists_board,player_healing_board,player_damage_board, invasion_winner, updating_invasion,player_rank, server)
                mycursor.execute(sql,val)
                print(val)
                mydb.commit()

        return(f"Stats have been updated for this invasion, ensure the changes are on the website here: https://www.nw-stats.com/{server}/invasion/{updating_invasion}")
    except:
        return(f"There was an error when trying to fix the stats for invasion {updating_invasion}, Please use the /deleteinvasion command to remove it from the site, correct any errors on the spreadsheet, then run the /enterinvasion command to add the invasion back to the website!")


def remove_duped_wars():
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    all_war_results = []
    mycursor = mydb.cursor()
    sql = "SELECT * FROM player_records"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for row in myresult:
        if row not in all_war_results:
            all_war_results.append(row)

    mycursor.execute("TRUNCATE player_records")
    for war_entry in all_war_results:
        data = (war_entry[0],war_entry[1],war_entry[2],war_entry[3],war_entry[4],war_entry[5],war_entry[6],war_entry[7],war_entry[8], war_entry[9], war_entry[10], war_entry[11], war_entry[12], war_entry[13], war_entry[14], war_entry[15])
        insert_stmt = (
        "INSERT INTO player_records(war_name, war_rank, name, score, kills, deaths, assists, healing, damage, war_id, war_link, k_par, dmg_kpar, team, war_winner, player_role)"
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        print(data)
        mycursor.execute(insert_stmt, data)
        mydb.commit()


def remove_war(server,war_num):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
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
    mycursor = mydb.cursor()
    sql = "SELECT * FROM player_records WHERE server = %s AND war_id = %s"
    val=(server,war_num)
    mycursor.execute(sql,val)
    myresult = mycursor.fetchall()
    for item in myresult:
        update_player_averages(item[2],server)
    sql = "DELETE FROM player_records WHERE server = %s AND war_id = %s"
    val = (server, war_num)
    mycursor.execute(sql, val)
    mydb.commit()

    return(f"War {war_num} has been removed from the website! Please correct all issues leading to the removal, and run the /enterstats command to readd it to the site!")

def remove_invasion(server,invasion_num):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
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
    mycursor = mydb.cursor()

    sql = "DELETE FROM invasion_records WHERE server = %s AND invasion_id = %s"
    val = (server, invasion_num)
    mycursor.execute(sql, val)
    mydb.commit()

    return(f"Invasion {invasion_num} has been removed from the website! Please correct all issues leading to the removal, and run the /enterinvasionstats command to readd it to the site!")