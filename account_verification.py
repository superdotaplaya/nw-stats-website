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


discord_id = "84172608601325568"
verified_name = "Deephaus"


def verify_account(discord_id,verified_name):
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
    print(myresult)
    id_found = False
    for row in myresult:
        print(row)
        if discord_id in row:
            id_found = True

    if id_found == True:
        sql = "UPDATE player_accounts SET verified = %s, verified_name = %s WHERE discord_id = %s"
        val = ('True',verified_name,discord_id)
        mycursor.execute(sql, val)
        mydb.commit()
        id_found = True
        print("User has been verified!")


    if id_found == False:
        print("User not found, double check their discord ID, or verify that the person has signed in on the website and setup their account first!")

verify_account(discord_id,verified_name)