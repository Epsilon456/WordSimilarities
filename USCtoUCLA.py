import Similarities as Sims
import pandas as pd
import Score
from sklearn.utils import shuffle
import os
import Setup



#Either launch the USC Crawler or load a checkpoint file if one exists.
if os.path.exists(Setup.pickleJar):
    import pickle
    with open(Setup.pickleJar,'rb') as f:
        List = pickle.load(f)
else:
    import USCCrawler2 as USCC
    List = USCC.USCCrawl()
    
#Either launch the USC cleaner or load a checkpoint file if one exists.

if os.path.exists(Setup.jsonFile):
    #Load a dataframe from a json file.
    import Setup
    jsonFile = Setup.jsonFile
    uscDF = pd.read_json(jsonFile,orient='index') 
else:
    
    import Cleaner
    #Run Cleaning script to generate dictionary
    Dictionary = Cleaner.Clean(List)
    #Convert dictionary into pandas dataframe.
    uscDF = pd.DataFrame.from_dict(Dictionary,orient='index')
    print("Cleaned Data")
   
    
#Either launch the UCLA Crawler and cleaner or load a checkpoint file if one exists.

if os.path.exists(Setup.UCLAClean):
    import json
    jsonFile = Setup.UCLAClean
    with open(jsonFile, 'r') as inFile:
        UCLADict = json.load(inFile)
else:
    import UCLACleaner
    import UCLAScraper
    
    UCLAScraper.UCLAScrape()
    UCLADict = UCLACleaner.UCLAClean()
  
#Convert the UCLADict to a dataframe
uclaDF = pd.DataFrame.from_dict(UCLADict,orient='index')

#Shuffle the usc data and only take the top 10
uscDF = shuffle(uscDF).head(10)
#Initialize and train the WordSim method using the UCLA data
S = Sims.Similarities(uclaDF,"Word")

import Score
#Go through 10 random USC courses
for course in uscDF.index:
    #Prompt user to navigate through loop.
    a = input("Press any key to randomly load a usc course:\nPress 'q' to quit")
    if a == 'a':
        break    
    #Obtain a list of scored ucla courses which are most similar to usc course.
    Vec = Score.SimScore(uclaDF,uscDF,course,S.WordSim)
    #print the data from the input usc course and the most relevant ucla course.
    print("\n")
    print("USC Course:\n")
    print(uscDF['name'][course],":\n")
    print(uscDF['description'][course])
    print("\n")
    print("Closest USC Course:\n")
    print(uclaDF["name"][Vec.head(1).index[0]],":\n")
    print(uclaDF['description'][Vec.head(1).index[0]])
    print("\n\n")

print("Done")
    

        