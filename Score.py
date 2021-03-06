import pandas as pd
import numpy as np

def SimScore(trainDF,testDF,incourse,method):
    """Iterates through the test courses in the test dataframe and compares them to the list courses
    in the training dataframe.  Produces a dataframe containing similarity scores which compare each list course 
    to the test course.  The dataframe will then be sorted from most similar to least similar.
    Inputs:
        trainDF - A pandas dataframe containing the training data. Frame will consist of columns 
            ('index','description','preqNames',and 'school') with rows consisting of the course 
            number indexes (all lowercase no colons.) 
        testDF - A pandas dataframe consisting of the test data. Frame will be in the same format as "trainDF"
        incourse - a string representing the desired course number.
        method - The function that is to be used to produce the similarity calculation.
            (method must take in a dataframe, and two strings representing course numbers.)
    Output:
        A sorted dataframe with one column (labeled the default "0") that is indexed by course numbers. Column 0 
        contains the similarity score between incourse and the course indexed in the dataframe. The dataframe is sorted
        from most similar to least similar. (Note: If the dataframe contains the incourse, the similarity score
        will be automatically set to zero to avoid matching with itself.
        
    """
    vec = {}
    #Go through each index in the dataframe and calculate the similarity between the row in the dataframe 
        #and the given course (incourse)
    for index, _ in trainDF.iterrows():
        if index != incourse:
            try:
                _vec = method(testDF,index,incourse)
                #Store the results to a dictionary indexed by course number.
                vec[index] = _vec
            except ValueError:
                vec[index] = 0


    #Convert the dictionary to a dataframe. Sort the dataframe by the similarity scores.
    Vec = pd.DataFrame.from_dict(vec,orient='index')
    Vec.sort_values(0,inplace=True,ascending=False)
    
    return Vec


def SchoolMetric(trainSet,testSet,incourse,Vec):
    """This is a metric used to determine how accurate the method for determining the of two courses is. 
    This will take in the top 10 courses with the highest similarity score and look at the school for each one (either "engineering" or "medicine").
    It will then determine how many of the top 10 courses are of the same school as the given course and calculate a percentage
    (as a decimal) to be used as a scoring metric.
    Inputs:
        trainSet - A pandas dataframe containing the train data (used for list courses). Frame will consist of columns 
            ('index','description','preqNames',and 'school') with rows consisting of the course 
            number indexes (all lowercase no colons.) 
        testSet - A pandas dataframe containing the test data. In the same format as trainSet
        incourse - a string representing the desired course number.
        Vec - A sorted dataframe containing a similarity score between each course and incourse. Dataframe will
            have one column (column "0") and will be indexed by course number.
    Output:
        A score between 0 and 1 (with one being the best score).
        
    """
    #Obtain the school for the given course, "incourse"
    inSchool = testSet['school'][incourse]
    metric = 0
    #Look at the schools for the top 10 most similar courses.
    for number in Vec.head(10).index:
        school = trainSet['school'][number]
        #If the school in the row of the dataframe is the same as incourse's school, then increment "metric" by 1.
        if school == inSchool:
            metric +=1
    #Divide by 10 (since there are 10 courses) to obtain the percentage.
    return metric/10

def PreqMetric(trainSet,testSet,incourse,Vec):
    """This is a metric used to determine how accurate the method for determining the similarity of two courses is.
    This will take in the top 3 courses from the train set (list courses which are most similar to the test course
    with the highest similarity score and look at the prerequisites for each. It will
    then calculate the percentage (as a decimal) of the match for the top 3.
    Inputs:
        trainSet - A pandas dataframe containing the train data. Frame will consist of columns 
            ('index','description','preqNames',and 'school') with rows consisting of the course 
            number indexes (all lowercase no colons.) 
        testSet - dataframe containing test data. In the same format as "trainSet"
        incourse - a string representing the desired course number.
        Vec - A sorted dataframe containing a similarity score between each course and incourse. Dataframe will
            have one column (column "0") and will be indexed by course number.
    Output:
        A score between 0 and 1 (with one being the best score)."""
        
    #Obtain the prerequisites for the given course as a set.
    inPreqs = set(testSet['preqName'][incourse])
    #Only proceed if the given course has prerequisites.
    if len(inPreqs) > 0:
        #"score" is the variable used to count how many preReqs in the course in the dataframe match the preReqs in the
            #given course.
        score = 0
        #Obtain the top 3 most similar clourses.
        for result in Vec.head(3).index:
            #Obtain a list of the prerequisites for the most similar course.
            resultPreqs = set(trainSet['preqName'][result])
            #Increment "score" by one for each prerequisite in the list that matches the set of prerequisites from"incourse".
            for rp in resultPreqs:
                if rp in inPreqs:
                    score +=1
        #Divide "score" by the number of possible prerequisites.
        return score/(3*len(inPreqs))
    #If "incourse" contains no prerequisites, then determine how many of the top 3 also contain no preReqs.
    else:
        score = 0
        #Obtain the top 3 most similar clourses.
        for result in Vec.head(3).index:
            #Determine how many preReqs are in each of the top 3 courses
            numPreqs = len(set(trainSet['preqName'][result]))
            #If this course also has 0 preReqs, then increment "score"
            if numPreqs == 0:
                score += 1
        #Divide score by 3 (the number of courses).
        return score/3
    
def ScoreMethod(trainSet,testSet,S,ScoreDict,iterations,numberTest=50):
    """Scores each of the 5 methods with each of the two scores. Saves the results to a dictionary.
    Inputs:
        testSet - A pandas dataframe containing the test data. Frame will consist of columns 
            ('index','description','preqNames',and 'school') with rows consisting of the course 
            number indexes (all lowercase no colons.)
        S - An instance of the "Similarities" class that has been instantiated with a trainSet dataframe.
            (This class contains all 5 methods for calculating similarity).
        ScoreDict - A nested dictionary containing the scores. (If this is the first iteration of the cross validation,
            these scores will all be 0 and will be updated by this function. If this is a subsequent iteration, then 
            the scores will be updated with a running average taking into account this iteration and all previous iterations.
            The outer dictionary will contain each of the 5 methods tested.
            The inner dictionaries will contain the two performance metrics.
        iterations - The number of iterations that are to be used in cross validation. (This is used to calculate
            a running average to save memory.)
    Outputs:
        An updated version of ScoreDict
    """
    #A dictionary connecting the name of each method to the function which calculates it.
    if S.GloveFail == False:
        Methods = {"Jacard":S.Jacard,"Lev":S.Lev,"WordSim":S.WordSim,"DocSim":S.DocSim,"GloveSim":S.GloveSim}
    else:
        Methods = {"Jacard":S.Jacard,"Lev":S.Lev,"WordSim":S.WordSim,"DocSim":S.DocSim}

       
    #Iterate over each method
    for methodName in Methods.keys():
        #Iterate over each course.
        for course in testSet.head(numberTest).index:
            #Calculate the similarity score for each course number in "testSet" and sort the list.
            Vec = SimScore(trainSet,testSet,course,Methods[methodName])


            #Calculate the accuracy of this scoring by using the two accuracy metrics.
            metS = SchoolMetric(trainSet,testSet,course,Vec)
            metP = PreqMetric(trainSet,testSet,course,Vec)
            print(course,methodName,metS,metP)
            
            #Take the average of each score by dividing each score by the total number of courses analyzed (over all 3 
                #iterations) and sum the quotients.
            ScoreDict[methodName]["School"] += (metS/(iterations*numberTest))
            ScoreDict[methodName]["Preq"] += (metP/(iterations*numberTest))
            
    return ScoreDict






