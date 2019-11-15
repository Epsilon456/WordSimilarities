import Similarities as Sims
import pandas as pd
import Score
from sklearn.utils import shuffle
"""This file serves as a wrapper which will call functions from all other scripts to run through the entire process of 
scraping, cleaning, evaluating, and scoring.
"""

def SplitData(df,trainRatio=.9):
    """Takes a dataframe, shuffles its rows, and splits it randomly into a training dataframe and a testing dataframe. 
    Inputs:
        df: A pandas dataframe that is to be split.
        trainRatio: The fraction of data to delegate to the training set
    Outputs:
        trainSet: A shuffled dataframe consisting of trainRatio of the rows of the original dataframe.
        testSet:  A shuffled dataframe consisting of 1-trainRatio of the rows of the original dataframe.
    """
    #A shuffled version of the original dataframe.
    ddf = shuffle(df)
    #Define the length of the original frame, the training frame, and the testing frame.
    length = len(ddf)
    trainLength = int(trainRatio*length)
    testLength = length-trainLength
    #Take the top and bottom portions of the shuffled frame to create two new frames.
    trainSet = ddf.head(trainLength)
    testSet = ddf.tail(testLength)
    
    return trainSet,testSet

#Ask the user to either re-crawl the USC course site or to load data from a previous crawl.
reCrawl = int(input("Re Crawl Site? \n0) No\n1) Yes"))
if reCrawl == 1:
    import USCCrawler2 as USCC

    #Run python script to crawl USC site.
    List = USCC.USCCrawl()
else:
    import pickle
    import Setup
    #Load a list of dictionaries from the pickle file.  Each dictionary will contain the following labels:
        #'name','number',description','school',and 'preq'
    with open(Setup.pickleJar,'rb') as f:
        List = pickle.load(f)
        
#Ask the user to either rerun the data cleaning script or to load data from a json file generated the last time the data was 
    #cleaned. Data will be in a dictionary that can be accessed by "Dictionary[number][label]"
    #where the "number" is the course number (all lowercase with no colon) and the label is one of the following:
    #'name','number',description','school',and 'preq'
reClean = int(input("Re Clean Data? \n0) No\n1) Yes"))
if reClean == 1:
    import Cleaner
    #Run Cleaning script to generate dictionary
    Dictionary = Cleaner.Clean(List)
    #Convert dictionary into pandas dataframe.
    df = pd.DataFrame.from_dict(Dictionary,orient='index')
    print("Cleaned Data")

else:
    #Load a dataframe from a json file.
    import Setup
    jsonFile = Setup.jsonFile
    df = pd.read_json(jsonFile,orient='index')    
  
#Create a dictionary of dictionaries to store the results from the cross validation
    #The outer dictionary will contain each of the 5 methods tested.
    #The inner dictionaries will contain the two performance metrics.
ScoreDict = {"Jacard":{},"Lev":{},"WordSim":{},"DocSim":{},"GloveSim":{}}
for sd in ScoreDict.keys():
    ScoreDict[sd] = {"School":0,"Preq":0}
    
iterations = 3
for i in range(iterations):
    #Randomly split data into training and test dataset at each iteration.
    trainSet,testSet = SplitData(df)
    #Initialize all 5 methods to be tested (2 of the 5 methods will take) will 
        #inititialize using the training data.
    S = Sims.Similarities(trainSet)
    #Score each method using the two performance metrics. ScoreDict will contain a score for 
        #each method-metric pair where 1.0 represents 100% accuracy.
    ScoreDict = Score.ScoreMethod(testSet,S,ScoreDict,iterations)
    print("Finished Cross Validation",i+1)
    
#Convert resuls to a pandas dataframe that can be easily displayed or saved to a file.
resultsFrame = pd.DataFrame.from_dict(ScoreDict,orient="index")
print(resultsFrame)




        