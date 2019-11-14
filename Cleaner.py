import Setup
import pickle
import re

    
def CleanDesc(text):
    text = text.lower()
    for StopPhrase in Setup.StopPhrases:
        text = re.sub(StopPhrase,'',text)
    for StopWord in Setup.StopWords:
        text = text.replace(StopWord," ")
    text = text.replace("  "," ")
    return text
def CleanName(text):
    text = text.lower()
    if text[0] == ' ':
        text =  text[1:]
    if text[-1] == ' ':
        text = text[:-1]
    return text
def CleanNumber(text):
    text = text.lower()
    text = text.replace(':','')
    return text

def Clean(List):
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
        

    import json
    jsonFile = Setup.jsonFile
    with open(jsonFile, 'w') as outfile:
        json.dump(Dictionary, outfile)
    print("Save dictionary as Json")
    return Dictionary




