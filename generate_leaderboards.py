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


from mysql.connector import Error

client_id = config.client_id
client_secret = config.client_secret
redirect_uri=config.redirect_uri
scope = config.scope
token_url = config.token_url
authorize_url = config.authorize_url

admin_list = config.admin_list

server_list = ['cos','del','val','mar','oro','ygg','eri']
player_list = []

mydb = mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_pass,
        database="superdotaplaya$war_stats"
        )


def generate_leaderboard():
    mycursor = mydb.cursor()
    sql = "SELECT * FROM player_records"
    mycursor.execute(sql)
    myresult =  mycursor.fetchall()
    for row in myresult:
        if row[2] not in player_list:
            player_list.append(row[2])
    leaderboards(player_list)

def leaderboards(player_list):
    mycursor = mydb.cursor()
    for server in server_list:

        for player in player_list:
            total_wars = 0
            player_scores = []
            player_kills = []
            player_assists = []
            player_healing = []
            player_damage = []
            sql = "SELECT * FROM player_records WHERE name = %s and server = %s"
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
                data = (player, server, player_avg_score, player_avg_kills, player_avg_assists, player_avg_healing, player_avg_damage, total_wars)
                insert_stmt = (
                "INSERT INTO player_averages(player_name, server, avg_score, avg_kills, avg_assists, avg_healing, avg_damage, total_wars)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                )
                print(data)
                mycursor = mydb.cursor()
                mycursor.execute(insert_stmt, data)
                mydb.commit()
            else:
                continue

generate_leaderboard()
