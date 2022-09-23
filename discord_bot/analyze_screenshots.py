from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os

import sys
import time
import pygsheets
def extract_text(images, war_name, server):
    gc = pygsheets.authorize(service_file='credentials.json')
    if not os.path.isfile("config.py"):
        sys.exit("'config.py' not found! Please add it and try again.")
    else:
        import config

    '''
    Authenticate
    Authenticates your credentials and creates a client.
    '''
    subscription_key = config.subscription_key
    endpoint = config.endpoint


    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(config.subscription_key))
    '''
    OCR: Read File using the Read API, extract text - remote
    This example will extract text in an image, then print results, line by line.
    This API call can also extract handwriting style text (not shown).
    '''
    print("===== Read File - remote =====")
    # Get an image with text
    players = []

    war_matchup = war_name
    read_image_urls = images
    print(images)
    read_image_urls.reverse()

    # Call API with URL and raw response (allows you to get the operation location)
    for url in read_image_urls:
        read_response = computervision_client.read(url,  raw=True)

        # Get the operation location (URL with an ID at the end) from the response
        read_operation_location = read_response.headers["Operation-Location"]
        # Grab the ID from the URL
        operation_id = read_operation_location.split("/")[-1]

        # Call the "GET" API and wait for it to retrieve the results
        while True:
            read_result = computervision_client.get_read_result(operation_id)
            if read_result.status not in ['notStarted', 'running']:
                break
            time.sleep(1)

        # Print the detected text, line by line
        if read_result.status == OperationStatusCodes.succeeded:
            player = []
            lines_read = 0

            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    if lines_read <= 7:
                        player.append(line.text)
                        lines_read += 1
                    else:
                        players.append(player)
                        lines_read = 0
                        player = []
                        player.append(line.text)
                        lines_read += 1
        players.append(player)
        print(players)
        print()

    if server.lower() == "cos":
        sh = gc.open('Testing war dumps')
    elif server.lower() == "ygg":
        sh = gc.open('YGG war records')
    elif server.lower() == "del":
        sh = gc.open('Delos war records')
    elif server.lower() == "val":
        sh = gc.open('Valhalla war records')
    elif server.lower() == "oro":
        sh = gc.open('Orofena war records')
    elif server.lower() == "mar":
        sh = gc.open('Maramma war records')
    elif server == "eri":
        sh = gc.open('Eridu war records')
    info = sh.worksheets()
    last_sheet = info[-1].title
    sh.add_worksheet(title=str(int(last_sheet)+1), rows=100, cols=26, src_tuple=None, src_worksheet=None, index=None)
    wks = sh.worksheet_by_title(str(int(last_sheet)+1))
    returned_values = wks.get_values_batch( ['A1:H250'] )
    print(returned_values[0])
    war_title = [int(last_sheet)+1, war_matchup]
    pygsheets.datarange.DataRange(start="A1", end="H1000", worksheet=wks).update_values(values=players)
    wks = sh.worksheet_by_title("War List")
    returned_values = wks.get_values_batch( ['A1:C500'] )
    returned_values[0].append(war_title)
    pygsheets.datarange.DataRange(start="A1", end="C1000", worksheet=wks).update_values(values=returned_values[0])
    return(f"Stats have been submitted! Go here to view this war's stats: http://www.nw-stats.com/{server.lower()}/war/{int(last_sheet)+1}")


        ## TODO figure out how to get it to link multiple images together before uplaoding to google spreadhsheet (prob loop through a list of images through a discord command then have Austin take that raw infomration from the spreadsheet and copy/paste it into the real stat tracking one!)