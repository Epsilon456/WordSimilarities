"""
This file contains all of the urls and filepathways used throughout this solution.
"""
#The URL to get to the UCS course catalog
url = r'https://classes.usc.edu/term-20193/'

#Preprocessing steps save data so that the entire code does not need to be run every time.

#The raw data saved after scraping the site
pickleJar = r'D:\Python Codes\Graph Theory\USCCourses\pickleFile.pkl'   
#A JSON file containing the clean data
jsonFile = r'D:\Python Codes\Graph Theory\USCCourses\jsonFile.json' 
#The pretrained word vectors downloaded from the glove dataset.
gloveJar = r'D:\Python Codes\Graph Theory\USCCourses\gloveJar.pkl'
