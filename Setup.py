"""
This file contains all of the urls and filepathways used throughout this solution.
"""
import os
#The URL to get to the UCS course catalog
url = r'https://classes.usc.edu/term-20193/'

#Preprocessing steps save data so that the entire code does not need to be run every time.
#rootFolder = r'D:\Python Codes\Graph Theory\USCCourses'
rootFolder = os.path.dirname(os.path.abspath(__file__))
#The raw data saved after scraping the site
pickleJar = os.path.join(rootFolder,"pickleFile.pkl")
#A JSON file containing the clean data
jsonFile = os.path.join(rootFolder,"jsonFile.json")
#The pretrained word vectors downloaded from the glove dataset.
gloveJar = os.path.join(rootFolder,"gloveJar.pkl")
