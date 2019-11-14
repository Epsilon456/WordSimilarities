import Levenshtein as LV
import gensim
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class Similarities:
    def __init__(self,df):
        self.df = df
            
        self._initText()
        self._initWordVec()
        self._initDocVec()
        self._initGloveVec()
        
    def _initText(self):
        #Get text from descriptions. The variable is a nested list where the outer list represents
        #each description and the inner list is each word in that description.
        self.texts = []
        for index, row in self.df.iterrows():
            self.texts.append(row['description'].split())
        print("Text initialized")
        
    def _initWordVec(self):
        self.WordVecModel = gensim.models.Word2Vec(self.texts,size=150,window=10,min_count=2,workers=4,iter=100)
        print("Word2Vec Model initialized")
    def _initDocVec(self):
        from gensim.models.doc2vec import Doc2Vec, TaggedDocument
        documents = []
        for i in range(len(self.texts)):
            documents.append(TaggedDocument(self.texts[i],[i]))
        self.DocVecModel = Doc2Vec(documents, vector_size=5, window=2, min_count=1, workers=4,epochs=100)
        print("Doc2Vec Model initialized")
    def _initGloveVec(self):
        import Setup
        import pickle
        import os
        if os.path.exists(Setup.gloveJar):
            with open(Setup.gloveJar,'rb') as f:
                word_vectors = pickle.load(f)
        else:
            "Maybe add an option to switch off pickle mode?"
            import gensim.downloader as api
            word_vectors = api.load("glove-wiki-gigaword-100") 
            with open(Setup.gloveJar,'wb') as f:
                pickle.dump(word_vectors,f)
            print("pickled word vectors download")
        self.gloveModel = word_vectors
        print("Glove model initialized")
            
    def Jacard(self,testDf,a,b):
        A = testDf['description'][a]
        B = testDf['description'][b]
        setA = set(A.split())
        setB = set(B.split())
        score = 0
        for a in setA:
            if a in setB:
                score +=1
        return score/(len(setA)+len(setB))

    def Lev(self,testDf,a,b):
        A = testDf['name'][a]
        B = testDf['name'][b]
        maxLen = max(len(A),len(B))
        return 1-LV.distance(A,B)/maxLen  
    
    def _WordSimAveVec(self,testDf,a):
        Description = testDf['description'][a].split()
        Vector = np.zeros(self.WordVecModel.layer1_size)
        wordCount = 0
        for word in Description:
            if word in self.WordVecModel.wv.vocab:
                vector = self.WordVecModel.wv.get_vector(word)
                Vector +=vector
                wordCount +=1
        return Vector/wordCount
    
    def WordSim(self,testDF,a,b):
        aVec = self._WordSimAveVec(testDF,a)
        bVec = self._WordSimAveVec(testDF,b)
        A = np.expand_dims(aVec,0)
        B = np.expand_dims(bVec,0)
        sim = cosine_similarity(A,B)
        return float(sim)
        
    
    def DocSim(self,testDf,a,b):
        textA = testDf['description'][a]
        textB = testDf['description'][b]
        
        vectorA = self.DocVecModel.infer_vector([textA], alpha=0.1, min_alpha=0.0001, steps=5)
        vectorB = self.DocVecModel.infer_vector([textB], alpha=0.1, min_alpha=0.0001, steps=5)
        
        A = np.expand_dims(vectorA,0)
        B = np.expand_dims(vectorB,0)
        sim = cosine_similarity(A,B)
        return float(sim)
    

    def _GloveSim(self,testDf,a):
        doc = testDf['description'][a]
        Vectors = []
        for word in doc:
            if word in self.gloveModel.vocab:
                vector = self.gloveModel.get_vector(word)
                Vectors.append(vector)
        Vectors = np.array(Vectors)
        sd = np.std(Vectors,axis=0)
        
        a0 = np.average(Vectors,axis=0)
        asd = a0+sd
        amax = np.max(Vectors,axis=0)
        amin = np.amin(Vectors,axis=0)
        
        return np.stack((a0,asd,amax,amin),1)
    
    def GloveSim(self,testDf,a,b):
        A = self._GloveSim(testDf,a).T
        B = self._GloveSim(testDf,b).T
        sim = cosine_similarity(A,B)
        result = np.average(np.diag(sim))
        return result
    
    


    
#test = Similarities()
#a = 'acmd 501'
#b = 'acmd 502'  
#test.GloveSim(a,b)
    
    
    
    






