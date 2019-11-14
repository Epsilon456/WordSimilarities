import USCCrawler2 as UCC
import Cleaner
import Similarities as Sims
import pandas as pd
import Score
from sklearn.utils import shuffle

def SplitData(df):
    ddf = shuffle(df)
    length = len(ddf)
    trainLength = int(.9*length)
    testLength = length-trainLength
    
    trainSet = ddf.head(trainLength)
    testSet = ddf.tail(testLength)
    
    return trainSet,testSet


#Get raw data
reCrawl = int(input("Re Crawl Site? \n0) No\n1) Yes"))
if reCrawl == 1:
    List = UCC.USCCrawl()
else:
    import pickle
    import Setup
    with open(Setup.pickleJar,'rb') as f:
        List = pickle.load(f)
        
        
reClean = int(input("Re Clean Data? \n0) No\n1) Yes"))
if reClean == 1:
    Dictionary = Cleaner.Clean(List)
    df = pd.DataFrame.from_dict(Dictionary,orient='index')
    print("Cleaned Data")

else:
    import Setup
    jsonFile = Setup.jsonFile
    df = pd.read_json(jsonFile,orient='index')    
  
ScoreDict = Score.ScoreDict

iterations = 3
for i in range(iterations):
    trainSet,testSet = SplitData(df)
    S = Sims.Similarities(trainSet)
    ScoreDict = Score.ScoreMethod(testSet,S,ScoreDict,iterations)
    print("Finished Cross Validation",i+1)
    
resultsFrame = pd.DataFrame.from_dict(ScoreDict,orient="index")
print(resultsFrame)




        