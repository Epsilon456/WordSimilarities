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
"""

class Similarities:
    """This class takes in a training data frame that is used to train the word2vec and doc2vec embeddings.  
    The 5 methods can the be called when passed the test data frame.
    """
    def __init__(self,df):
        #The input training data frame.
        self.df = df
        #Transforms the text strings from the descriptions into a list of list of words.
        self._initText()
        #Initializes and trains the word2vec embeddings.
        self._initWordVec()
        #Initializes and trains the doc2vec embeddigns.
        self._initDocVec()
        #Loads in the pretrained GloVe data.
        self._initGloveVec()
        
    def _initText(self):
        #Get text from descriptions. The variable is a nested list where the outer list represents
        #each description and the inner list is each word in that description.
        self.texts = []
        for index, row in self.df.iterrows():
            self.texts.append(row['description'].split())
        print("Text initialized")
        
    def _initWordVec(self):
        #Load the list of list consisting of the course descriptions into the word2vec model. Train the model
        self.WordVecModel = gensim.models.Word2Vec(self.texts,size=150,window=10,min_count=2,workers=4,iter=100)
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
        self.DocVecModel = Doc2Vec(documents, vector_size=150, window=10, min_count=2, workers=4,epochs=100)
        print("Doc2Vec Model initialized")
    def _initGloveVec(self):
        #Initializes the pre-trained GloVe model.
        import Setup
        import pickle
        import os
        #If the model has already been saved, import it from the pickle file and store to the variabe "word_vectors"
        if os.path.exists(Setup.gloveJar):
            with open(Setup.gloveJar,'rb') as f:
                word_vectors = pickle.load(f)
        #If the model has not already been saved, call the api downloader to download the model.
        else:
            "Maybe add an option to switch off pickle mode?"
            import gensim.downloader as api
            word_vectors = api.load("glove-wiki-gigaword-100") 
            #Once the model has been downloaded, save the word_vectors as a pickle file for later use.
            with open(Setup.gloveJar,'wb') as f:
                pickle.dump(word_vectors,f)
            print("pickled word vectors download")
        #Allow word vectors to be accessed by other methods in the class.
        self.gloveModel = word_vectors
        print("Glove model initialized")
            
    def Jacard(self,testDf,a,b):
        """Calculates the Jacard similarity between two course descriptions.
        Inputs:
            testDF - The test dataframe consisting of columns ('index','description','preqNames',and 'school') with rows
                consisting of the course number indexes (all lowercase no colons.)
            a,b - each of these is a string representing the course number.
        Outputs:
            The Jacard similarity score scaled between 0 and 1.
        """
        #Obtain the course descriptions for the two course indexes inputed into the function.
        A = testDf['description'][a]
        B = testDf['description'][b]
        #Create a set of words for each description.
        setA = set(A.split())
        setB = set(B.split())
        
        #Count the number of words in set a that are also in set b.
        score = 0
        for a in setA:
            if a in setB:
                score +=1
        #Divide the number by the total length of both sets.
        return score/(len(setA)+len(setB))

    def Lev(self,testDf,a,b):
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
        A = testDf['name'][a]
        B = testDf['name'][b]
        #Figure out the length of the longest course name.
        maxLen = max(len(A),len(B))
        #Calculate the compliment of the normalized Levenshtein distance.  
        return 1-LV.distance(A,B)/maxLen  
    
    def _WordSimAveVec(self,testDf,a):
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
        Description = testDf['description'][a].split()
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
    
    def WordSim(self,testDF,a,b):
        """Calculate the cosine similarity between two vectors where each vector represents a course
        description. Each vector is made by taking the average of each word vector that makes up the description. Average
        vectors are calculated by a helper method "_WordSimAveVec"
        Inputs:
            testDF - A test dataframe consisting of columns ('index','description','preqNames',and 'school') with rows
                consisting of the course number indexes (all lowercase no colons.) 
            a,b - A string representing the course number
        """
        #Obtain a single vector embedding for each course description (calculated by taking an average of each word 
            #embedding that makes up each description)
        aVec = self._WordSimAveVec(testDF,a)
        bVec = self._WordSimAveVec(testDF,b)
        #Convert vectors to column vectors to be fed into the cosine_similarity function.
        A = np.expand_dims(aVec,0)
        B = np.expand_dims(bVec,0)
        #Calculate the cosine similarity between the two vectors.
        sim = cosine_similarity(A,B)
        return float(sim)
        
    
    def DocSim(self,testDf,a,b):
        """Calculate the cosine similarity between two document vectors.
        Inputs:
            testDF - A test dataframe consisting of columns ('index','description','preqNames',and 'school') with rows
                consisting of the course number indexes (all lowercase no colons.) 
            a,b - A string representing the course number"""
        #Obtain the descriptions of the two input courses.
        textA = testDf['description'][a]
        textB = testDf['description'][b]
        
        #Obtain the document embedding vector for each description.
        vectorA = self.DocVecModel.infer_vector([textA], alpha=0.1, min_alpha=0.0001, steps=5)
        vectorB = self.DocVecModel.infer_vector([textB], alpha=0.1, min_alpha=0.0001, steps=5)
        
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
    
    def GloveSim(self,testDf,a,b):
        """Calculate the cosine similarity between two document arrays.
        Inputs:
            testDF - A test dataframe consisting of columns ('index','description','preqNames',and 'school') with rows
                consisting of the course number indexes (all lowercase no colons.) 
            a,b - A string representing the course number
        Outputs
            Cosine similarity"""
        #Obtain the matrix representation of the document encoding for each description. Transpose the matricies
        A = self._GloveSim(testDf,a).T
        B = self._GloveSim(testDf,b).T
        
        #Take the cosine similarity of these two matricies. This creates a 4x4 matrix where each row represents
            #one of the four categories (mean,stdev,max,min) of one course description and each column represents one of the four
            #of the other course description.
        sim = cosine_similarity(A,B)
        #The diagonal of this 4x4 matrix is a comparision of like categories across the two different course descriptions.
            #By taking the average of this diagonal, a similarity score can be obtained.
        result = np.average(np.diag(sim))
        return result
    
    


    
#test = Similarities()
#a = 'acmd 501'
#b = 'acmd 502'  
#test.GloveSim(a,b)
    
    
    
    






