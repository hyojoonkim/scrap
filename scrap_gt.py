import os
import sys
import datetime
import json
import logging
import urllib2
from bs4 import BeautifulSoup
import python_api

def scrap_gt():

    resultMapList = []


    baseUrl = 'https://support.cc.gatech.edu/alerts'
    resultMapListOnePage = scrap_page(baseUrl)

    if len(resultMapListOnePage) !=0 :
        resultMapList.extend(resultMapListOnePage)

    # Next page. page=1 is the second page, which is strange. Whatever.
    page = 1
    while 1:
        resultMapListOnePage = scrap_page(baseUrl + '?page='+str(page))

        if len(resultMapListOnePage) !=0 :
            resultMapList.extend(resultMapListOnePage)
            page = page + 1

        else: 
            print 'Likely ended. Abort.'
            break


    print len(resultMapList)
    sys.setrecursionlimit(10000)
    python_api.save_data_as_pickle(resultMapList, 'resultMapList', './')


    return

def scrap_page(url):
    resultMapList = []

    result = urllib2.urlopen(url)
    html = result.read();
    soup = BeautifulSoup(html)
    tbody = soup.find_all('tbody')

    if len(tbody)!=1:
        print "Cannot find tbody. Skip"
        return {}

    else:
        tb = tbody[0]
        types = tb.find_all('td', {'class':'views-field views-field-field-alert-type'})

    # Go through every item in this page
    for t in types:
        resultMap = {'ton':'','title':'','desc':'','startTime':'','endTime':''}

        ## Type of Notice
        typeOfNotice = t.contents[0].replace('\n','').encode("ascii").lstrip(' ').rstrip(' ')
        resultMap['ton'] = typeOfNotice

        ## Title
        nextT = t.findNext('td',{'class':'views-field views-field-title'})
        if nextT:
            title = nextT.find('a', href=True).contents[0]
            resultMap['title'] = title
        else:
            print 'No title'
        
        ## Description
        nextT = nextT.findNext('td',{'class':'views-field views-field-field-alert-description'})
        if nextT:
            desc = nextT.contents[0].replace('\n','').encode("ascii").lstrip(' ').rstrip(' ')
            resultMap['desc'] = desc
        else:
            print 'No Description'
 
        ## Start date
        nextT = nextT.findNext('td',{'class':'views-field views-field-field-alert-start active'})

        if nextT:
            nextT = nextT.findNext('span', {'class':'date-display-single'})
            if nextT:
                startTime= nextT.contents[0].replace('\n','').encode("ascii").lstrip(' ').rstrip(' ')
                resultMap['startTime'] = startTime
            else:
                print 'No start date'
        else:
            print 'No start date'
 
        ## End date
        nextT = nextT.findNext('td',{'class':'views-field views-field-field-alert-end'})

        if nextT:
            nextT = nextT.findNext('span', {'class':'date-display-single'})
            if nextT:
                endTime= nextT.contents[0].replace('\n','').encode("ascii").lstrip(' ').rstrip(' ')
                resultMap['endTime'] = endTime
            else:
                print 'No end date'
        else:
            print 'No end date'
        resultMap

        resultMapList.append(resultMap)

    # Return results in this page
    return resultMapList


def main():
    scrap_gt()

if __name__ == '__main__':
    main()

