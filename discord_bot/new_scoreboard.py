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



def get_groups(image):
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
    endpoint = "https://nw-scoreboards.cognitiveservices.azure.com/"

    model_id = "Scoreboard_neural"
    formUrl = "https://cdn.discordapp.com/attachments/1050600656915927060/1055302919999729834/8f9di0ywxcTMAAAAAASUVORK5CYII.png"

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential("69e5be691f8b4977aa041e1095273c50")
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


            print(name, field.value)


get_groups("https://media.discordapp.net/attachments/1081670149150609476/1081670160076779570/image15.jpg")


