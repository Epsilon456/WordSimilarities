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

def USCCrawl():
    """Crawls the USC course catalog to pull course names, course numbers, course descriptions, and 
    prerequisite courses for all engineering and medicine courses. Stores each course as a dictionary of with the labels 'name','number',
    'description','school',and 'preq'.  All course dictionaries are stored in one list.  The list is then
    saved (using python's pickle library) to checkpoint the process.
        
    """
    
    
    print("Crawling course catalog: \n\n")
    url = Setup.url
    tree = GetPage(url)
    schools = ["Engineering","Medicine"]
    List = []
    
    #The first page of the course catalog lists all of the schools. The crawler must first navigate 
        #to the desired school.
    for school in schools:
        #Find the link to the desired school
        A = tree.xpath('/html/body/div[3]/div/div[1]/ul[2]/li[contains(@data-school,"'+school+'")]')
        for a in A:
            #Follow the link to the desired school and get the page for the school.
            link = a.xpath('.//a')[0].values()[0]
            tree1 = GetPage(link)
            #Store the information contained in the next page.
            courses = tree1.xpath('//div[contains(@class,"course-info expandable")]')
            
            #For each course, get the name,number,description, and prerequisite list.
            for course in courses:
                courseName = course.xpath('.//h3/a/text()')[0].title()
                courseNumber = course.xpath('.//a/strong/text()')[0].title()
                courseDes = course.xpath('.//div[1]/text()')[0].title()
                _coursePreqLink = course.xpath('.//div[2]/ul/li[contains(@class,"prereq")]/a[1]')
                _coursePreqName = course.xpath('.//div[2]/ul/li[contains(@class,"prereq")]/a/text()')
    
                #Courses can have zero or many prerequisites.  Store these as a list.
                coursePreqLink = []
                coursePreqName = []
                for c in _coursePreqLink:
                    coursePreqLink.append(c.values()[0])
                for n in _coursePreqName:
                    coursePreqName.append(n.title())
                    
                #Organize data into a dictionary
                dictionary = {'name':courseName,'number':courseNumber,'description':courseDes,'preqLink':coursePreqLink,'preqName':coursePreqName,'school':school}
                #Append dictionary to a master list.
                List.append(dictionary)
     
    #Save the raw list data as a pickle file.
    pickleJar = Setup.pickleJar    
    import pickle    
    # open a file, where you ant to store the data
    file = open(pickleJar, 'wb')
    # dump information to that file
    pickle.dump(List, file)
    # close the file
    file.close()
    print("file pickled")
    #Return the raw list.
    return List
    
    
