from lxml import html
import requests
import random as rand
import time
import Setup


def GetPage(url):
    time.sleep(rand.uniform(.7,4.0))
    
    page = requests.get(url)
    tree = html.fromstring(page.content)
    print(url)
    return tree
def USCCrawl():
    print("Crawling course catalog: \n\n")
    url = Setup.url
    tree = GetPage(url)
    schools = ["Engineering","Medicine"]
    List = []
    
    for school in schools:
        A = tree.xpath('/html/body/div[3]/div/div[1]/ul[2]/li[contains(@data-school,"'+school+'")]')
        for a in A:
            link = a.xpath('.//a')[0].values()[0]
                
            tree1 = GetPage(link)
            
            courses = tree1.xpath('//div[contains(@class,"course-info expandable")]')
            
            
            for course in courses:
                courseName = course.xpath('.//h3/a/text()')[0].title()
                courseNumber = course.xpath('.//a/strong/text()')[0].title()
                courseDes = course.xpath('.//div[1]/text()')[0].title()
                _coursePreqLink = course.xpath('.//div[2]/ul/li[contains(@class,"prereq")]/a[1]')
                _coursePreqName = course.xpath('.//div[2]/ul/li[contains(@class,"prereq")]/a/text()')
    
                coursePreqLink = []
                coursePreqName = []
                for c in _coursePreqLink:
                    coursePreqLink.append(c.values()[0])
                for n in _coursePreqName:
                    coursePreqName.append(n.title())
            
                dictionary = {'name':courseName,'number':courseNumber,'description':courseDes,'preqLink':coursePreqLink,'preqName':coursePreqName,'school':school}
                List.append(dictionary)
     
    pickleJar = Setup.pickleJar    
    import pickle    
    # open a file, where you ant to store the data
    file = open(pickleJar, 'wb')
    # dump information to that file
    pickle.dump(List, file)
    # close the file
    file.close()
    print("file pickled")
    return List
    
    
