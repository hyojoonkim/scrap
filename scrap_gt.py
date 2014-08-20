#################################################
# Copyright 2014 Hyojoon Kim
# All Rights Reserved 
# 
# email: deepwater82@gmail.com
#################################################

import os
import sys
import datetime
import json
import logging
import urllib2
from bs4 import BeautifulSoup
import python_api
import datetime
import re

def find_dates(content, resultMap):
    start_date = ''
    end_date = ''

    month_union = '(January|February|March|April|May|June|July|August|September|October|November|December)'
    m = re.findall(month_union + ' (\d+), (\d\d\d\d)', content)
    if len(m) == 0:
        print 'Failed to find dates:', resultMap['url']
        
    elif len(m) == 1:
        start_s = m[0][0] + ' ' + m[0][1] + ', ' + m[0][2]
        sdate = datetime.datetime.strptime(start_s, '%B %d, %Y')
        start_date = sdate.strftime('%Y-%m-%d ')
        end_date = sdate.strftime('%Y-%m-%d ')
       
    elif len(m) == 2:
        start_s = m[0][0] + ' ' + m[0][1] + ', ' + m[0][2]
        end_s = m[1][0] + ' ' + m[1][1] + ', ' + m[1][2]
        sdate = datetime.datetime.strptime(start_s, '%B %d, %Y')
        edate = datetime.datetime.strptime(end_s, '%B %d, %Y')
        start_date = sdate.strftime('%Y-%m-%d ')
        end_date = edate.strftime('%Y-%m-%d ')

    # time
    m2 = re.findall('(\d+):(\d\d) (PM|AM)*', content)
    if len(m2)==0:
        print 'No time'
        if start_date!='':
            start_date = start_date + '01:00'
        if end_date!='':
            end_date = end_date + '23:00'

    elif len(m2) ==1:
        time = ''
        if m2[0][2] == 'PM' and m2[0][0]!='12':
            time = str(int(m2[0][0]) + 12) + ':' + m2[0][1]
        else:
            if len(m2[0][0])==1:
                time = '0'
            time = time + m2[0][0] + ':' + m2[0][1]

        if start_date!='':
            start_date = start_date + time
        if end_date!='':
            end_date = end_date + '23:00'
        
    elif len(m2) >=2 :
        stime = ''
        if m2[0][2] == 'PM' and m2[0][0]!='12':
            stime = str(int(m2[0][0]) + 12) + ':' + m2[0][1]
        else:
            if len(m2[0][0])==1:
                stime = '0'
            stime = stime + m2[0][0] + ':' +  m2[0][1]

        if start_date!='':
            start_date = start_date + stime
 
        etime = ''
        if m2[-1][2] == 'PM' and m2[-1][0]!='12':
            etime = str(int(m2[-1][0]) + 12) + ':' + m2[-1][1]
        else:
            if len(m2[-1][0])==1:
                etime = '0'
            etime = etime + m2[-1][0] + ':' + m2[-1][1]

        if end_date!='':
            end_date = end_date + etime

    print content
    print start_date
    print end_date
    return start_date, end_date

def deal_with_bogus_entry(nextT, resultMap):
    print resultMap
    result = urllib2.urlopen('https://support.cc.gatech.edu'+resultMap['url'])
    html = result.read();
    soup = BeautifulSoup(html)
    desc = soup.find('div', {'class':'field-item even'})
    
    start_date, end_date = find_dates(str(desc.contents[0]), resultMap)

    if start_date!='' and end_date!='':
        resultMap['startTime'] = start_date
        resultMap['endTime'] = end_date

    return

def scrap_gt():

    resultMapList = []
    baseUrl= 'https://support.cc.gatech.edu/alerts?order=field_alert_start&sort=desc'
    resultMapListOnePage = scrap_page(baseUrl)

    if len(resultMapListOnePage) !=0 :
        resultMapList.extend(resultMapListOnePage)

    # Next page. page=1 is the second page, which is strange. Whatever.
    page = 1
    while 1:
        resultMapListOnePage = scrap_page(baseUrl + '&page='+str(page))

        if len(resultMapListOnePage) !=0 :
            resultMapList.extend(resultMapListOnePage)
            page = page + 1

        else: 
            print 'Likely ended. # of pages=',page,'. Abort.'
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
            t = nextT.find('a', href=True)
            title = t.contents[0]
            url = t['href']
            resultMap['title'] = title.encode("ascii")
            resultMap['url'] = url.encode("ascii")
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
                # Bogus entry
#                if startTime.startswith('2012-03-29 14:'):
#                    deal_with_bogus_entry(nextT,resultMap)

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
                # Bogus entry
                if endTime.startswith('2012-03-29 14:'):
                    deal_with_bogus_entry(nextT,resultMap)

            else:
                print 'No end date'
        else:
            print 'No end date'

        resultMapList.append(resultMap)

    # Return results in this page
    return resultMapList


def main():
    scrap_gt()

if __name__ == '__main__':
    main()

