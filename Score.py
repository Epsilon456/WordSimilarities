import pandas as pd
import numpy as np
def SimScore(df,incourse,method):
    vec = {}
    for index, _ in df.iterrows():
        _vec = method(df,incourse,index)
        if vec == 1.0:
            vec = 0.0
        vec[index] = _vec


    Vec = pd.DataFrame.from_dict(vec,orient='index')
    Vec.sort_values(0,inplace=True,ascending=False)
    
    return Vec


def SchoolMetric(df,incourse,Vec):
    inSchool = df['school'][incourse]
    metric = 0
    for number in Vec.head(10).index:
        school = df['school'][number]
        if school == inSchool:
            metric +=1
    return metric/10

def PreqMetric(df,incourse,Vec):
    inPreqs = set(df['preqName'][incourse])
    if len(inPreqs) > 0:
        score = 0
        for result in Vec.head(3).index:
            resultPreqs = set(df['preqName'][result])
           
            for rp in resultPreqs:
                if rp in inPreqs:
                    score +=1
        return score/(3*len(inPreqs))
    else:
        import numpy as np
        return 1.0
    
ScoreDict = {"Jacard":{},"Lev":{},"WordSim":{},"DocSim":{},"GloveSim":{}}
for sd in ScoreDict.keys():
    ScoreDict[sd] = {"School":0,"Preq":0}
    
def ScoreMethod(testSet,S,ScoreDict,iterations):
    Methods = {"Jacard":S.Jacard,"Lev":S.Lev,"WordSim":S.WordSim,"DocSim":S.DocSim,"GloveSim":S.GloveSim}
       
    for methodName in Methods.keys(): 
        for course in testSet.index:
            Vec = SimScore(testSet,course,Methods[methodName])
            metS = SchoolMetric(testSet,course,Vec)
            metP = PreqMetric(testSet,course,Vec)
            print(course,methodName,metS,metP)
            
            ScoreDict[methodName]["School"] += (metS/(iterations*len(testSet)))
            ScoreDict[methodName]["Preq"] += (metP/(iterations*len(testSet)))
        ScoreDict[methodName]["School"] = np.array(ScoreDict[methodName]["School"])
        ScoreDict[methodName]["Preq"] = np.array(ScoreDict[methodName]["Preq"])
    
    return ScoreDict






