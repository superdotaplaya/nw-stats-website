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
server = "COS"


gc = pygsheets.authorize(service_file='credentials.json')
def get_player_info():
    sh = gc.open('blacktunastats.com player responses')
    wks = sh.worksheet_by_title("Form Responses 1")
    returned_values = wks.get_values_batch( ['A2:E1000'] )
    return(returned_values[0])


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

def add_war():
    gc = pygsheets.authorize(service_file='credentials.json')

    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )

    mycursor = mydb.cursor()
    if server == "COS":
        sh = gc.open('Testing war dumps')
    elif server == "YGG":
        sh = gc.open('YGG war records')
    elif server == "DEL":
        sh = gc.open('Delos war records')
    elif server == "VAL":
        sh = gc.open('Valhalla war records')
    info = sh.worksheets()
    sheet_id = int(info[-1].title)

    sheet_title = info[-1].title
    wks = sh.worksheet_by_title(str(sheet_title))
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
        if int(war_item[0]) == int(sheet_id):
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
    response = beams_client.publish_to_interests(
      interests=['hello'],
      publish_body={
        'apns': {
          'aps': {
            'alert': {
              'title': 'Hello',
              'body': 'Hello, world!',
            },
          },
        },
        'fcm': {
          'notification': {
            'title': 'Hello',
            'body': 'Hello, world!',
          },
        },
        'web': {
          'notification': {
            'title': 'New War Entered on Black Tuna Stats!',
            'body': f"{war_name}",
            'deep_link': f"https://www.blacktunastats.com/{server.lower()}/war/{war_id}",
          },
        },
      },
    )

    print(response['publishId'])

def fix_stats(updating_war):
    gc = pygsheets.authorize(service_file='credentials.json')

    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )

    mycursor = mydb.cursor()

    if server == "COS":
        sh = gc.open('Testing war dumps')
    elif server == "YGG":
        sh = gc.open('YGG war records')
    elif server == "DEL":
        sh = gc.open('Delos war records')
    elif server == "VAL":
        sh = gc.open('Valhalla war records')
    wks = sh.worksheet_by_title(updating)
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
        if int(war_number[0]) == int(updating):
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
        else:
            sql = "UPDATE player_records SET war_name = %s, war_rank = %s, name = %s, score = %s, kills = %s, deaths = %s, assists = %s, healing = %s, damage = %s, dmg_kpar = %s, team = %s, war_winner = %s WHERE war_id = %s AND war_rank = %s AND server = %s"
            val = (war_name,player_rank,player_name,player_score_board,player_kills_board,player_deaths_board,player_assists_board,player_healing_board,player_damage_board, "N/A", round(dmg_kpar,2), player[9], war_winner, updating_war,player_rank, server)
            mycursor.execute(sql,val)
            print(val)

            mydb.commit()

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




def remove_war(war_id):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    sql = "DELETE FROM player_records WHERE war_id = %s"
    val = (war_id,)
    mycursor.execute(sql, val)
    mydb.commit()


