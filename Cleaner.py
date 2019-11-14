import Setup
import pickle
import re

"""
This file contains the functions used to clean the data from the webcrawler. Such cleaning
includes moving all strings into lower case and stop word removal.
"""
#The regular expressions to remove from the course descriptions
#Two re's are contained here. The first is a repeated phrase "open only to _ majors"
#The second is when the prerequisite courses are copied in the description.
StopPhrases = ["Open Only To .+ Majors",r'\w{2,3,4}\s{1}\d{3}.']
#Words and symbols to remove from the text
StopWords = [".",";",":","/",' a ',' of ',' the ',"prerequisite","or","at","to","will","are","be"]
    
def CleanDesc(text):
    """Cleans the description text
    """
    #Convert all text to lowercase
    text = text.lower()
    #Remove regular expression phrases
    for StopPhrase in StopPhrases:
        text = re.sub(StopPhrase,'',text)
    #Remove stopwords
    for StopWord in StopWords:
        text = text.replace(StopWord," ")
    #Remove long spaces caused by the first two steps.
    text = text.replace("  "," ")
    #Return the cleaned text
    return text
def CleanName(text):
    """Cleans the string representing the course name.
    """
    #Convert all text to lowercase.
    text = text.lower()
    #If a space is the first or last character, remove the space.
    if text[0] == ' ':
        text =  text[1:]
    if text[-1] == ' ':
        text = text[:-1]
    #Return cleaned text
    return text
def CleanNumber(text):
    """Cleans the string representing the course number
    """
    #Convert all text to lowercase
    text = text.lower()
    #Remove the ":"
    text = text.replace(':','')
    return text

def Clean(List):
    """Takes in the list of dictionaries from the webcrawler and applies cleaning functions
    to each part.  Converts list into a Dictionary which is indexed by the course number.
    Saves a copy of the dictionary to a json file
    Inputs: A list of dictionaries containing 'name','number','description','preqName','school'
    Outputs: A dictionary that can be accessed by Dictionary[number][label]
    """
    Dictionary = {}
    for item in List:
        description = CleanDesc(item['description'])
        name = CleanName(item['name'])
        number = CleanNumber(item['number'])
        school = item['school']
        preqName = []
        for pn in item['preqName']:
            preqName.append(CleanNumber(pn))
        Dictionary[number] = {'name':name,'description':description,'preqName':preqName,'school':school}
        
    #Save dictionary to json file.
    import json
    jsonFile = Setup.jsonFile
    with open(jsonFile, 'w') as outfile:
        json.dump(Dictionary, outfile)
    print("Save dictionary as Json")
    return Dictionary




