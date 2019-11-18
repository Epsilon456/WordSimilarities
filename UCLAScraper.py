from lxml import html
import requests
import random as rand
import time
import Setup

"""
This script contains the scraper which pulls the relevant data from USC's course catalog.
"""

def GetPage(url):
    """Pulls the html from the webpage. Adds a random delay between web page calls.
    Input:
        url - A string representing the desired url to visit
    Output
        An html tree
    """
    #Adds random delay (to avoid overworking the server)
    time.sleep(rand.uniform(.7,4.0))
    page = requests.get(url)
    tree = html.fromstring(page.content)
    print(url)
    return tree

def UCLAScrape():
    """Scrapes course data from the UCLA course catalog and returns a dictionary
    containing {'name':[],'description':[]}
    A copy of this dictionary is saved as a json file.
    """
    
    #Scrape the page containing all schools.
    url = r'https://www.registrar.ucla.edu/Academics/Course-Descriptions'
    baseUrl = r'https://www.registrar.ucla.edu/'
    page = GetPage(url)
    things = page.xpath('//td[contains(@style,"width:50%;")]')
    Schools = {'school':[],'href':[]}
    #Iterate through all schools and save their paths to a list.
    for thing in things:
        name = thing.xpath('.//li/a/text()')[0].title()
        _href = name = thing.xpath('.//li/a')[0].values()[0]
        href = baseUrl+_href
        
        Schools['school'].append(name)
        Schools['href'].append(href)
        
        print(name)
    
    i = 0
    myDictionary = {'name':[],'description':[]}
    #Go through each path from the first page
    for url in Schools['href']:
        print(url)
        print(i,"/",len(Schools['href']))
        i +=1
        #Get the page from the given path.
        page = GetPage(url)
        
        #Go through each course, save the name and description to a dictionary.
        courses = page.xpath('//li[contains(@class,"media category-list-item")]')
        for course in courses:
            try:
                name = course.xpath('.//div/h3/text()')[0].title()
                descripton = course.xpath('.//p[2]/text()')[0].title()
                myDictionary['name'].append(name)
                myDictionary['description'].append(descripton)
            except IndexError:
                pass
    
    #Save dictionary to json file.
    import json
    jsonFile = Setup.UCLA
    with open(jsonFile, 'w') as outfile:
        json.dump(myDictionary, outfile)
    print("Save dictionary as Json")
