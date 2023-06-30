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



def add_message(server,message,company):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    data = (company, message, server)
    insert_stmt = (
                "INSERT INTO recruitment(company_name, message, server)"
                "VALUES (%s, %s, %s)"
                )
    mycursor.execute(insert_stmt, data)
    mydb.commit()

def delete_message(server, company):
    mydb = mysql.connector.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_pass,
    database="superdotaplaya$war_stats"
    )
    mycursor = mydb.cursor()
    data = (company, server)
    insert_stmt = "DELETE FROM recruitment WHERE company_name = %s AND server = %s"

    mycursor.execute(insert_stmt, data)
    mydb.commit()
