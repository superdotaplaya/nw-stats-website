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
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import config
import pygsheets


#from PIL import Image
bot = discord.Bot()


gc = pygsheets.authorize(service_file='credentials.json')
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config

gc = pygsheets.authorize(service_file='credentials.json')

wrong_names = [["cOrruption", "c0rrupti0n"], ["corruption","c0rruption"], ["JMoose 1231", "JMoose1231"],["Jmoose 1231","JMoose1231"],["xerOstatus","xer0status"], ["xerostatus","xer0status"], ["milkyway1 up","milkyway1up"],["FastAs Thunder","FastAsThunder"],["Thaumaturge 1","Thaumaturge1"],["PopeNelaBaraja","PopeNeiaBaraja"],["Wild","W1ld"],["bobo","9bob9"]]



def get_groups(image, war_id, event_name):
    gc = pygsheets.authorize(service_file='credentials.json')
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
    """
    Remember to remove the key from your code when you're done, and never post it publicly. For production, use
    secure methods to store and access your credentials. For more information, see
    https://docs.microsoft.com/en-us/azure/cognitive-services/cognitive-services-security?tabs=command-line%2Ccsharp#environment-variables-and-application-configuration
    """
    subscription_key = config.subscription_key
    endpoint = "https://nw-stats-form.cognitiveservices.azure.com/"

    model_id = "Current_Model"
    formUrl = "https://cdn.discordapp.com/attachments/1050600656915927060/1055302919999729834/8f9di0ywxcTMAAAAAASUVORK5CYII.png"

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential("cbc6168e9a224c348d1c149dbf484978")
    )

    # Make sure your document's type is included in the list of document types the custom model can analyze
    poller = document_analysis_client.begin_analyze_document_from_url(model_id, image)
    result = poller.result()

    for idx, document in enumerate(result.documents):
        print("--------Analyzing document #{}--------".format(idx + 1))
        print("Document has type {}".format(document.doc_type))
        print("Document has confidence {}".format(document.confidence))
        print("Document was analyzed by model with ID {}".format(result.model_id))

        for name, field in document.fields.items():
            player_name = field.value
            for wrong_name in wrong_names:
                if player_name == wrong_name[0]:
                    player_name = wrong_name[1]
            if name.rstrip().lstrip() == "player 1" or name ==  "player 2" or name == "player 3" or name == "player 4" or name == "player 5":
                print(name)
                group1.append(player_name)
            elif name.rstrip().lstrip() == "player 6" or name == "player 7" or name == "player 8" or name == "player 9" or name == "player 10":
                group2.append(player_name)
            elif name.rstrip().lstrip() == "player 11" or name == "player 12" or name ==  "player 13" or name == "player 14" or name == "player 15":
                group3.append(player_name)
            elif name.rstrip().lstrip() == "player 16" or name == "player 17" or name == "player 18" or name == "player 19" or name == "player 20":
                group4.append(player_name)
            elif name.rstrip().lstrip() == "player 21" or name == "player 22" or name ==  "player 23" or name == "player 24" or name == "player 25":
                group5.append(player_name)
            elif name.rstrip().lstrip() == "player 26" or name == "player 27" or name == "player 28" or name == "player 29" or name == "player 30":
                group6.append(player_name)
            elif name.rstrip().lstrip() == "player 31" or name == "player 32" or name == "player 33" or name == "player 34" or name == "player 35":
                group7.append(player_name)
            elif name.rstrip().lstrip() == "player 36" or name == "player 37" or name == "player 38" or name == "player 39" or name == "player 40":
                group8.append(field.value)
            elif name.rstrip().lstrip() == "player 41" or name == "player 42" or name == "player 43" or name == "player 44" or name == "player 45":
                group9.append(player_name)
            elif name.rstrip().lstrip() == "player 46" or name == "player 47" or name == "player 48" or name == "player 49" or name == "player 50":
                group10.append(player_name)
    sh = gc.open('Sinaloa Payouts and Attendance')
    all_groups = [group1,group2,group3,group4,group5,group6,group7,group8,group9,group10]
    wks = sh.worksheet_by_title(f"Week {war_id}")
    print(wks.get_values_batch(["A2:J66"])[0][0])
    if (not wks.get_values_batch(["A2:J66"])[0][0]) or wks.get_values_batch(["A2:J66"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="A2", end="E11", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="A1", end="A1", worksheet=wks).update_values(values=[[event_name]])
    elif (not wks.get_values_batch(["F2:J66"])[0][0]) or wks.get_values_batch(["F2:J66"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="F2", end="J11", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="F1", end="F1", worksheet=wks).update_values(values=[[event_name]])
    elif (not wks.get_values_batch(["A13:J66"])[0][0]) or wks.get_values_batch(["A13:J66"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="A13", end="J22", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="A12", end="A12", worksheet=wks).update_values(values=[[event_name]])
    elif (not wks.get_values_batch(["F13:J66"])[0][0]) or wks.get_values_batch(["F13:J66"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="F13", end="J22", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="F12", end="F12", worksheet=wks).update_values(values=[[event_name]])
    elif (not wks.get_values_batch(["A24:J66"])[0][0]) or wks.get_values_batch(["A24:J66"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="A24", end="E33", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="A23", end="A23", worksheet=wks).update_values(values=[[event_name]])
    elif (not wks.get_values_batch(["F24:J66"])[0][0]) or wks.get_values_batch(["F24:J66"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="F24", end="J33", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="F23", end="F23", worksheet=wks).update_values(values=[[event_name]])
    elif (not wks.get_values_batch(["A35:J66"])[0][0]) or wks.get_values_batch(["A35:J66"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="A35", end="E44", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="A34", end="A34", worksheet=wks).update_values(values=[[event_name]])
    elif (not wks.get_values_batch(["F35:J66"])[0][0]) or wks.get_values_batch(["F35:J66"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="F35", end="J44", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="F34", end="F34", worksheet=wks).update_values(values=[[event_name]])
    elif (not wks.get_values_batch(["A46:J66"])[0][0]) or wks.get_values_batch(["A46:J66"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="A46", end="E55", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="A45", end="A45", worksheet=wks).update_values(values=[[event_name]])
    elif (not wks.get_values_batch(["F46:J66"])[0][0]) or wks.get_values_batch(["F46:J66"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="F46", end="J55", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="F45", end="F45", worksheet=wks).update_values(values=[[event_name]])
    elif (not wks.get_values_batch(["A57:J66"])[0][0]) or wks.get_values_batch(["A57:J66"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="A57", end="E66", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="A56", end="A56", worksheet=wks).update_values(values=[[event_name]])
    elif (not wks.get_values_batch(["F57:J66"])[0][0]) or wks.get_values_batch(["F57:J66"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="F57", end="J66", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="F56", end="F56", worksheet=wks).update_values(values=[[event_name]])
    elif (not wks.get_values_batch(["A68:E77"])[0][0]) or wks.get_values_batch(["A68:E77"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="A68", end="E77", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="A67", end="A67", worksheet=wks).update_values(values=[[event_name]])
    elif (not wks.get_values_batch(["F68:J77"])[0][0]) or wks.get_values_batch(["F68:J77"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="F68", end="J77", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="F67", end="F67", worksheet=wks).update_values(values=[[event_name]])
    elif (not wks.get_values_batch(["A79:E88"])[0][0]) or wks.get_values_batch(["A79:E88"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="A78", end="E88", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="F56", end="F56", worksheet=wks).update_values(values=[[event_name]])
    elif (not wks.get_values_batch(["F79:J88"])[0][0]) or wks.get_values_batch(["F79:J88"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="F57", end="J66", worksheet=wks).update_values(values=all_groups)
        pygsheets.datarange.DataRange(start="F56", end="F56", worksheet=wks).update_values(values=[[event_name]])
    print(wks.get_values_batch(["F35:J66"])[0][0])


@bot.slash_command(description = "Add an event to the weekly payout sheet.")
async def addevent(ctx, week_number: Option(str, "What week is this event being added to?"), event_name: Option(str, "What is the name of this event?")):
    await ctx.respond("Attempting to add event, please wait a moment!")
    images = []

    messages = await ctx.channel.history(limit=200).flatten()
    for message in messages:
        print(message.content)
        for link in reversed(message.attachments):
            images.append(link.url)
    image = images[0]
    get_groups(image,week_number, event_name)
    await ctx.send(f"'{event_name}' has been logged for this weeks payouts this week!")


@bot.slash_command(description = "Add a push to the weekly payout sheet.")
async def addpush(ctx, week_number: Option(str, "What week is this push being added to?"), push_name: Option(str, "What is the name of this push?"), channel_name: Option(discord.TextChannel, channel_types=[discord.ChannelType.forum])):
    await ctx.respond("Attempting to add event, please wait a moment!")
    threads = channel_name.threads
    pushers = []
    sh = gc.open('Sinaloa Payouts and Attendance')
    wks = sh.worksheet_by_title(f"Week {week_number}")
    for thread in threads:
        messages = await thread.history(limit=100).flatten()
        pusher = thread.name
        for message in messages:
            print(message.content)
            message_user = await message.guild.fetch_member(message.author.id)
            if message_user.get_role(1097871662902431744):
                try:
                    missions_completed = int(message.content)
                    pushers.append([pusher,missions_completed])
                except:
                    pass
    print(pushers)
    if (not wks.get_values_batch(["A90:B160"])[0][0]) or wks.get_values_batch(["A90:B266"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="A90", end="B160", worksheet=wks).update_values(values=pushers)
        pygsheets.datarange.DataRange(start="A89", end="A89", worksheet=wks).update_values(values=[[push_name]])
    elif (not wks.get_values_batch(["C90:D160"])[0][0]) or wks.get_values_batch(["C90:D266"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="C90", end="D160", worksheet=wks).update_values(values=pushers)
        pygsheets.datarange.DataRange(start="C89", end="C89", worksheet=wks).update_values(values=[[push_name]])
    elif (not wks.get_values_batch(["E90:F160"])[0][0]) or wks.get_values_batch(["E90:F266"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="E90", end="F160", worksheet=wks).update_values(values=pushers)
        pygsheets.datarange.DataRange(start="E89", end="E89", worksheet=wks).update_values(values=[[push_name]])
    elif (not wks.get_values_batch(["G90:H160"])[0][0]) or wks.get_values_batch(["G90:H266"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="G90", end="H160", worksheet=wks).update_values(values=pushers)
        pygsheets.datarange.DataRange(start="G89", end="G89", worksheet=wks).update_values(values=[[push_name]])
    elif (not wks.get_values_batch(["I90:J160"])[0][0]) or wks.get_values_batch(["I90:J266"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="I90", end="J160", worksheet=wks).update_values(values=pushers)
        pygsheets.datarange.DataRange(start="I89", end="I89", worksheet=wks).update_values(values=[[push_name]])
    elif (not wks.get_values_batch(["A161:B240"])[0][0]) or wks.get_values_batch(["A161:B240"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="A161", end="B240", worksheet=wks).update_values(values=pushers)
        pygsheets.datarange.DataRange(start="A160", end="A160", worksheet=wks).update_values(values=[[push_name]])
    elif (not wks.get_values_batch(["C161:D240"])[0][0]) or wks.get_values_batch(["C161:D240"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="C161", end="D240", worksheet=wks).update_values(values=pushers)
        pygsheets.datarange.DataRange(start="C160", end="C160", worksheet=wks).update_values(values=[[push_name]])
    elif (not wks.get_values_batch(["E161:F240"])[0][0]) or wks.get_values_batch(["E161:F240"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="E161", end="F240", worksheet=wks).update_values(values=pushers)
        pygsheets.datarange.DataRange(start="E160", end="E160", worksheet=wks).update_values(values=[[push_name]])
    elif (not wks.get_values_batch(["G161:H240"])[0][0]) or wks.get_values_batch(["G161:H240"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="G161", end="H240", worksheet=wks).update_values(values=pushers)
        pygsheets.datarange.DataRange(start="G160", end="G160", worksheet=wks).update_values(values=[[push_name]])
    elif (not wks.get_values_batch(["I161:J240"])[0][0]) or wks.get_values_batch(["I161:J240"])[0][0] == ['']:
        pygsheets.datarange.DataRange(start="I161", end="J240", worksheet=wks).update_values(values=pushers)
        pygsheets.datarange.DataRange(start="I160", end="I160", worksheet=wks).update_values(values=[[push_name]])
    await ctx.send(f"'{push_name}' has been logged for this weeks payout!")

bot.run(config.discord_token_payouts)



#run the bot
 #Get your bot token from https://discordapp.com/developers/applications/

