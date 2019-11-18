import Levenshtein as LV
import gensim
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
"""This script contains a single class which in turn, contains all 5 of the methods to be tested (as well as their 
initialization functions.)  The five methods are as follows:
    1) Jacard Similarity between course descriptions 
    2) Leveshtein Distance between course names
    3) Similarity of the average Word2Vec encoding of course descriptions
    4) Similarity of the Doc2Vec encodings of course descriptions.
    5) Similarity of the "matrix" encoding using the pretrained GloVe encodings.
        (The matrix encoding is a concatenation of 4 encoding vectors.
        1) The average of all word vector encodings in the description.)
        2) The average + 1 st dev of all vector encodings
        3) A vector consisting of the max values of all vector encodings
        4) A vector consisting of the min values of all vector encodings.
    
    The methods used to to call these are as follows:
        Jacard
        Lev
        WordSim
        DocSim
        GloveSim
"""

class Similarities:
    """This class takes in a training data frame that is used to train the word2vec and doc2vec embeddings.  
    The 5 methods can the be called when passed the test data frame.
    Initialize this class with:
        trainDF - The dataframe used to train the embeddings.  This will also be the dataframe from which
            the program will pull the course closest to the test course.
        Mode - Either "All" for initializing all 5 methods or "Word" for only initializing "WordSim"
    """
    def __init__(self,trainDF,mode="All"):
        self.GloveFail = False
        self.mode = mode
        #The input training data frame.

        self.trainDF = trainDF
        #Transforms the text strings from the descriptions into a list of list of words.
        self._initText()
        #Initializes and trains the word2vec embeddings.
        self._initWordVec()
        #Only initialize DocSim and GloveSim if required.
        if mode == "All":
            #Initializes and trains the doc2vec embeddigns.
            self._initDocVec()
            #Loads in the pretrained GloVe data.
            self._initGloveVec()
        #Build a dictionary containing the embeddings for each description. This make it so that the 
            #the embedding functions only need to be called once for the test course which will then 
            #be compared to the embeddings in this dictionary.
        self.VDF = {"Word":{},"Doc":{},"Glove":{}}
        self._BuildSims()
        
        
    def _initText(self):
        #Get text from descriptions. The variable is a nested list where the outer list represents
        #each description and the inner list is each word in that description.
        self.texts = []
        for index, row in self.trainDF.iterrows():
            self.texts.append(row['description'].split())
        print("Text initialized")
        
    def _initWordVec(self):
        #Load the list of list consisting of the course descriptions into the word2vec model. Train the model
        self.WordVecModel = gensim.models.Word2Vec(self.texts,size=300,window=5,min_count=2,workers=4,iter=100)
        print("Word2Vec Model initialized")
    def _initDocVec(self):
        #Initializes and trains the doc2vec embedding
        from gensim.models.doc2vec import Doc2Vec, TaggedDocument
        documents = []
        #Iterate through each course description and store each as a tagged docuent. Create list of 
            #tagged documents.
        for i in range(len(self.texts)):
            documents.append(TaggedDocument(self.texts[i],[i]))
        #Train the doc2vec model with the tagged documents.
        self.DocVecModel = Doc2Vec(documents, vector_size=300, window=5, min_count=2, workers=4,epochs=100)
        print("Doc2Vec Model initialized")
    def _initGloveVec(self):
        #Initializes the pre-trained GloVe model.
        import Setup
        import pickle
        import os
        #If the model has already been saved, import it from the pickle file and store to the variabe "word_vectors"
        if os.path.exists(Setup.gloveJar):
            with open(Setup.gloveJar,'rb') as f:
                glove = pickle.load(f)
                self.gloveModel = glove

        #If the model has not already been saved, call the api downloader to download the model.
        else:
            print("Downloading GloVe word embeddings with gensim...")
            "Maybe add an option to switch off pickle mode?"
            try:
                import gensim.downloader as api
                glove = api.load("glove-wiki-gigaword-100") 

                #Once the model has been downloaded, save the word_vectors as a pickle file for later use.
                with open(Setup.gloveJar,'wb') as f:
                    pickle.dump(glove,f)
                print("word vectors saved to .pkl file")
                self.gloveModel = glove
                print("Glove model initialized")
            except:
                print("Glove Sim model failed to download")
                self.GloveFail = True
        #Allow word vectors to be accessed by other methods in the class.

            
    def Jacard(self,testDf,listCourse,inCourse):
        """Calculates the Jacard similarity between two course descriptions.
        Inputs:
            testDF - The test dataframe consisting of columns ('index','description','preqNames',and 'school') with rows
                consisting of the course number indexes (all lowercase no colons.)
            a,b - each of these is a string representing the course number.
        Outputs:
            The Jacard similarity score scaled between 0 and 1.
        """
        #Obtain the course descriptions for the two course indexes inputed into the function.
        A = self.trainDF['description'][listCourse]
        B = testDf['description'][inCourse]
        #Create a set of words for each description.
        setA = set(A.split())
        setB = set(B.split())
        
        #Count the number of words in set a that are also in set b.
        score = 0
        for a in setA:
            if a in setB:
                score +=1
        #Divide the number by the total length of both sets.
        return score/(len(setA.union(setB)))

    def Lev(self,testDf,listCourse,inCourse):
        """Calculates the Levenshtein distance between two course names.
        Inputs:
            testDF - The test dataframe consisting of columns ('index','description','preqNames',and 'school') with rows
                consisting of the course number indexes (all lowercase no colons.)
            a,b - each of these is a string representing the course number.
        Outputs:
            The compliment of the normalized Levenshtein distance
            (The compliment is calculated by 1-(L/D) where L is the Levenshtein distance and D is the length of the 
            longer of the two strings)
            This number is scaled between 0 and 1 where 1 represents a perfect match.
        """
        #Obtain the couse names for the two courses provided
        A = self.trainDF['name'][listCourse]
        B = testDf['name'][inCourse]
        #Figure out the length of the longest course name.
        maxLen = max(len(A),len(B))
        #Calculate the compliment of the normalized Levenshtein distance.  
        return 1-LV.distance(A,B)/maxLen  
    
    def _WordSimAveVec(self,df,a):
        """Calculates the a document embedding vector by taking the average of all word vectors in the document. This is
        a helper function to be used with the "WordSim" method.
        Inputs:
            testDF - A test dataframe consisting of columns ('index','description','preqNames',and 'school') with rows
                consisting of the course number indexes (all lowercase no colons.) 
            a - A string representing the course number
        Output:
            A vector embedding representing the entire document.
        """
        #Obtain the course description for the course provided and convert the string into a list of individual words.
        Description = df['description'][a].split()
        #Create a placeholder zero vector of the same size as the vector embedding.
        Vector = np.zeros(self.WordVecModel.layer1_size)
        wordCount = 0
        #Iterate over each word in the description.
        for word in Description:
            #If the word is in the trained vocabulary, obtain the word vector. 
            #Continue to add the word vectors to the placeholder vector to get the running sum.
            if word in self.WordVecModel.wv.vocab:
                vector = self.WordVecModel.wv.get_vector(word)
                Vector +=vector
                #Keep track of how many word vectors (which were included in the vocabulary) were added.
                wordCount +=1
        #Calculate the mean by dividing the sum by the number of vectors.
        return Vector/wordCount
    
    def _BuildSims(self):
        """Builds up the dictionary "self.VDF" to contain all of the document vector embeddings which are in 
        the training dataset to act as a reference. This way, the references only need to be calculated once.
        The method will build up the dictionary using 3 "columns" - one for each word embedding if "All" mode
        was selected for initializing the class.  If "Word" mode was selected, it will only build the dictionary
        for the "WordSim" method.
        Dictionary will be in the form VDF[Method][courseName]
        """
        if self.mode == "All":
            #Iterate through all rows of the training dataframe.
            for index, _ in self.trainDF.iterrows():
                #Obtain the document embeddings for each method.
                wordVec = self._WordSimAveVec(self.trainDF,index)
                docVec = self._DocSim(self.trainDF,index)
                #Save the embeddings to a dictionary
                self.VDF["Word"][index] = wordVec
                self.VDF["Doc"][index] = docVec
                if self.GloveFail == False:
                    gloveVec = self._GloveSim(self.trainDF,index)
                    self.VDF["Glove"][index] = gloveVec
        if self.mode == "Word":
            for index, _ in self.trainDF.iterrows():
                wordVec = self._WordSimAveVec(self.trainDF,index)
                self.VDF["Word"][index] = wordVec
          
    
    def WordSim(self,testDF,listCourse,inCourse):
        """Calculate the cosine similarity between two vectors where each vector represents a course
        description. Each vector is made by taking the average of each word vector that makes up the description. Average
        vectors are calculated by a helper method "_WordSimAveVec"
        Inputs:
            testDF - A test dataframe consisting of columns ('index','description','preqNames',and 'school') with rows
                consisting of the course number indexes (all lowercase no colons.) 
            listCourse - A string containing the course number of the reference course in the trainSet
            inCourse - A string containing the course number of the input test course.
        """
        #Obtain a single vector embedding for each course description (calculated by taking an average of each word 
            #embedding that makes up each description)
            
        #Get the embedding from the dictionary for the list (reference) course
        aVec = self.VDF["Word"][listCourse]
        #Calculate the embedding with the doc2Vec model.
        bVec = self._WordSimAveVec(testDF,inCourse)
        #Convert vectors to column vectors to be fed into the cosine_similarity function.
        A = np.expand_dims(aVec,0)
        B = np.expand_dims(bVec,0)
        #Calculate the cosine similarity between the two vectors.
        sim = cosine_similarity(A,B)
        return float(sim)
        
    def _DocSim(self,df,a):
        """Calculate the cosine similarity between two document vectors.
        Inputs:
            testDF - A test dataframe consisting of columns ('index','description','preqNames',and 'school') with rows
                consisting of the course number indexes (all lowercase no colons.) 
            a - A string representing the course number"""
        #Obtain the descriptions of the two input courses.
        textA = df['description'][a]
        #Obtain the document embedding vector for each description.
        vectorA = self.DocVecModel.infer_vector([textA], alpha=0.1, min_alpha=0.0001, steps=300)
        return vectorA
    
    def DocSim(self,testDF,listCourse,inCourse):
        """Calculates a vector embedding for a course description using the doc2vec method.
        Inputs:
            testDF  - A test dataframe consisting of columns ('index','description','preqNames',and 'school') with rows
                consisting of the course number indexes (all lowercase no colons.) 
            listCourse - A string containing the course number of the reference course in the trainSet
            inCourse - A string containing the course number of the input test course.
        """
        #Reference the VDF dictionary to get the doc embedding for the listCourse
        vectorA = self.VDF["Doc"][listCourse]
        #Calculate the doc embedding for the input course
        vectorB = self._DocSim(testDF,inCourse)
        
        #Convert vectors to column vectors to be fed into the cosine_similarity function. 
        A = np.expand_dims(vectorA,0)
        B = np.expand_dims(vectorB,0)
        #Calculate the cosine similarity between the two vectors.
        sim = cosine_similarity(A,B)
        return float(sim)
        

    def _GloveSim(self,testDf,a):
        """Uses the word vectors from the pre-trained GloVe model to generate an array representing the document. 
        Inputs:
            testDF - A test dataframe consisting of columns ('index','description','preqNames',and 'school') with rows
                consisting of the course number indexes (all lowercase no colons.) 
            a - A string representing the course number
        Outputs:
            An array consistingof the mean, standard deviation, min and maximum of all word vector embeddings which 
            make up the course description."""
        #Obtain the course description for the given course number.
        doc = testDf['description'][a]
        #Iterate over each word in the document. For each word in the GloVe vocab, append the word vector to a list
        Vectors = []
        for word in doc:
            if word in self.gloveModel.vocab:
                vector = self.gloveModel.get_vector(word)
                Vectors.append(vector)
        #Turn the list of vectors into an array.
        Vectors = np.array(Vectors)
        
        #Calculate the mean, mean+1stdev, maximum, and minimum of this array (each operation reducing 
            #the array to eliminate rows). Concatenate these 4 measures into one matrix to serve as an index for a 
            #document.
        sd = np.std(Vectors,axis=0)
        a0 = np.average(Vectors,axis=0)
        asd = a0+sd
        amax = np.max(Vectors,axis=0)
        amin = np.amin(Vectors,axis=0)
        
        return np.stack((a0,asd,amax,amin),1)
    
    def GloveSim(self,testDf,listCourse,inCourse):
        """Calculate the cosine similarity between two document arrays.
        Inputs:
            testDF - A test dataframe consisting of columns ('index','description','preqNames',and 'school') with rows
                consisting of the course number indexes (all lowercase no colons.) 
            listCourse - A string containing the course number of the reference course in the trainSet
            inCourse - A string containing the course number of the input test course.
        Outputs
            Cosine similarity"""
        #Obtain the matrix representation of the document encoding for each description. Transpose the matricies
        
        #Obtain the embedding from the dictionary for the list course
        A = self.VDF['Glove'][listCourse].T
        #Calculate the embedding for the input course using the GloVe model.
        B = self._GloveSim(testDf,inCourse).T
        
        #Take the cosine similarity of these two matricies. This creates a 4x4 matrix where each row represents
            #one of the four categories (mean,stdev,max,min) of one course description and each column represents one of the four
            #of the other course description.
        sim = cosine_similarity(A,B)
        #The diagonal of this 4x4 matrix is a comparision of like categories across the two different course descriptions.
            #By taking the average of this diagonal, a similarity score can be obtained.
        result = np.average(np.diag(sim))
        return result
    
    

#            School      Preq
#Jacard    0.762222  0.497531
#Lev       0.730000  0.475926
#WordSim   0.820000  0.517284
#DocSim    0.592222  0.444444
#GloveSim  0.598889  0.503704
    
