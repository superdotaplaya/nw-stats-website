"""
This code sample shows Custom Model operations with the Azure Form Recognizer client library.
The async versions of the samples require Python 3.6 or later.

To learn more, please visit the documentation - Quickstart: Form Recognizer Python client library SDKs
https://docs.microsoft.com/en-us/azure/applied-ai-services/form-recognizer/quickstarts/try-v3-python-sdk
"""

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import config
import pygsheets



def get_groups(image, war_id, server, attack_or_defense):
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
        endpoint=endpoint, credential=AzureKeyCredential("azure_key")
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


            if name.rstrip().lstrip() == "player 1" or name ==  "player 2" or name == "player 3" or name == "player 4" or name == "player 5":
                print(name)
                group1.append(field.value)
            elif name.rstrip().lstrip() == "player 6" or name == "player 7" or name == "player 8" or name == "player 9" or name == "player 10":
                group2.append(field.value)
            elif name.rstrip().lstrip() == "player 11" or name == "player 12" or name ==  "player 13" or name == "player 14" or name == "player 15":
                group3.append(field.value)
            elif name.rstrip().lstrip() == "player 16" or name == "player 17" or name == "player 18" or name == "player 19" or name == "player 20":
                group4.append(field.value)
            elif name.rstrip().lstrip() == "player 21" or name == "player 22" or name ==  "player 23" or name == "player 24" or name == "player 25":
                group5.append(field.value)
            elif name.rstrip().lstrip() == "player 26" or name == "player 27" or name == "player 28" or name == "player 29" or name == "player 30":
                group6.append(field.value)
            elif name.rstrip().lstrip() == "player 31" or name == "player 32" or name == "player 33" or name == "player 34" or name == "player 35":
                group7.append(field.value)
            elif name.rstrip().lstrip() == "player 36" or name == "player 37" or name == "player 38" or name == "player 39" or name == "player 40":
                group8.append(field.value)
            elif name.rstrip().lstrip() == "player 41" or name == "player 42" or name == "player 43" or name == "player 44" or name == "player 45":
                group9.append(field.value)
            elif name.rstrip().lstrip() == "player 46" or name == "player 47" or name == "player 48" or name == "player 49" or name == "player 50":
                group10.append(field.value)

    print(f"Group 1 : {group1}")
    print(f"Group 2 : {group2}")
    print(f"Group 3 : {group3}")
    print(f"Group 4 : {group4}")
    print(f"Group 5 : {group5}")
    print(f"Group 6 : {group6}")
    print(f"Group 7 : {group7}")
    print(f"Group 8 : {group8}")
    print(f"Group 9 : {group9}")
    print(f"Group 10 : {group10}")


    sh = gc.open(f'{server} Rosters')
    all_groups = [group1,group2,group3,group4,group5,group6,group7,group8,group9,group10]
    try:
        sh.add_worksheet(title= war_id, rows=100, cols=26, src_tuple=None, src_worksheet=None, index=None)
    except:
        wks = sh.worksheet_by_title(war_id)
        if attack_or_defense == "Attack":
            pygsheets.datarange.DataRange(start="A1", end="E10", worksheet=wks).update_values(values=all_groups)
        elif attack_or_defense == "Defense":
            pygsheets.datarange.DataRange(start="A12", end="E21", worksheet=wks).update_values(values=all_groups)
        return(group1,group2,group3,group4,group5,group6,group7,group8,group9,group10)


