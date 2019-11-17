import Setup
#Save dictionary to json file.
def UCLAClean():
    """Cleans the scraped data from the UCLAScraper. returns the results in a dictionary containing the "columns"
    'name','description' and 'preqName' and the "rows" with the course number labels.  The function returns the
    dictionary and saves a copy of it to a json file.
    """
    import json
    #Open the json file containing the raw scraped data.
    jsonFile = Setup.UCLA
    with open(jsonFile, 'r') as inFile:
        myDictionary = json.load(inFile)
    print("Load dictionary as Json")
    
    #The UCLA course data usually has a sentence at the beginning of the course description describing how long
        #the course is and a sentence at the end describing grading. This is irrelevant to the true course description
        #and must be removed.
    stopPhrases = ["hour","grading"]
    
    outDict = {}
    #Common words and characters to remove.
    removals = [".",";",":","/",' a ',' of ',' the '," or "," at "," to "," will "," are "," be ","(",")"]
    
    for i in range(len(myDictionary['description'])):
        #convert course descriptions to lowercase
        item = myDictionary['description'][i]
        item = item.lower()
        #Split the sentences
        sentences = item.split(".")
        preqs = ''
        cleanDes = ''
        #Go through each sentence. Only consider sentences that do not contain "stopPhrases"
        for sentence in sentences:
            if stopPhrases[0] not in sentence and stopPhrases[1] not in sentence:
                #Append the sentences to the proper string.
                cleanDes += sentence
                preqs += sentence
        #Remove unwanted characters/words from description.
        for removal in removals:
            cleanDes = cleanDes.replace(removal,'')
        #Convert the name to lower case
        tag = myDictionary['name'][i].lower()
        #The course names are actually the course number and course name separated by a period. Split these by 
            #the period.
        tags = tag.split(".")
        number = tags[0]
        #Start with a blank name and build up the string.
        name = ''
        
        #If the course name has periods in it, the name will split. Append everything from here onwards to a single
            #string.
        for i in range(len(tags)-1):
            name+=tags[i+1]
        #If a space is the first or last character, remove the space.
        if name[0] == ' ':
            name =  name[1:]
        if name[-1] == ' ':
            name = name[:-1]       
        
        if len(cleanDes) >1:
            if cleanDes[0] == ' ':
                cleanDes =  cleanDes[1:]
            if cleanDes[-1] == ' ':
                cleanDes = cleanDes[:-1]  
        

        #Save the dictionary portion.
        outDict[number] = {'name':name,'description':cleanDes,'preqName':preqs}

    #Save dictionary to json file.
    import json
    jsonFile = Setup.UCLAClean
    with open(jsonFile, 'w') as outfile:
        json.dump(outDict, outfile)
    print("Save dictionary as Json")
    return outDict

#UCLAClean()
        
                