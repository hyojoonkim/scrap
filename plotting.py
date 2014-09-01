#################################################
# Copyright 2014 Hyojoon Kim
# All Rights Reserved 
# 
# email: deepwater82@gmail.com
#################################################


import os
from optparse import OptionParser
import python_api
import plot_lib
import sys
import pickle
import time
import datetime
import numpy



def distance_cal(typename, data):

    iter_done = False
    distList = []

    for idx,i in enumerate(data):

        typeOfNotice = i['ton']
        if typeOfNotice!=typename:
            continue

        start = i['startTime']
        start_ts = python_api.checkTimeFormatReturn(start,'%Y-%m-%d %H:%M')
        if start_ts is None:
            if start.endswith('(All day)'):
                start_ts = fix_if_all_day(start,True)
            else: 
                print 'Wrong time format: ',start
                continue
        start_year_str = str(start_ts.year)    

        # Skip if 2007 or 2014
        if start_year_str =='2007' or start_year_str=='2014':
            continue

        # CDF of distance between each notice
        iter_done = False
        if idx < len(data)-1:
            idx_m = idx
            while 1:
                next_m = data[idx_m+1]
                if next_m['ton']==typename:
                    break
                idx_m = idx_m + 1
                if idx_m >= len(data)-1:
                    iter_done = True
                    break
 
            if iter_done is False:
                nxm_start = next_m['startTime']
                nm_start_ts = python_api.checkTimeFormatReturn(nxm_start,'%Y-%m-%d %H:%M')
                if nm_start_ts is None:
                    if nxm_start.endswith('(All day)'):
                        nm_start_ts = fix_if_all_day(nxm_start,True)
                    else: 
                        print 'Wrong time format: ',nxm_start
                        continue
   
                # diff
                tdistance = start_ts - nm_start_ts
                if tdistance.total_seconds() < 0:
                     print 'Bogus diff ca: ',start_ts,nm_start_ts,idx
                     pass
                elif tdistance.total_seconds() ==0 and start.startswith('2012-03-29 14:'):
#                     print 'Skip 2012/3/29:',start_ts,nm_start_ts,idx
                     pass
 
                else: 
                    dist = float(tdistance.total_seconds())/3600.0 #hours
                    distList.append(dist)

    return distList


def increment_map(theMap, key):
    if theMap.has_key(key):
        theMap[key] = theMap[key] + 1
    else:
        theMap[key] = 1


def fix_if_all_day(t_str,isStart):
    if isStart:
        forged = t_str.rstrip(' (All day)') + ' 01:00'
    else:
        forged = t_str.rstrip(' (All day)') + ' 23:00'
    t_ts = python_api.checkTimeFormatReturn(forged,'%Y-%m-%d %H:%M')
    if t_ts is None:
        print 'Wrong time format: ',forged
 
    return t_ts

def resort(data):  

    fix_data = []
    m = {}

    for idx,d in enumerate(data):
        start = d['startTime']
        start_ts = python_api.checkTimeFormatReturn(start,'%Y-%m-%d %H:%M')
        if start_ts is None:
            if start.endswith('(All day)'):
                start_ts = fix_if_all_day(start,True)
            else: 
                print 'Wrong time format: ',start
                continue

        timestamp = (start_ts - datetime.datetime(1970, 1, 1)).total_seconds()

        if m.has_key(timestamp):
            timestamp = timestamp + 1
            m[timestamp] = idx
        else:
            m[timestamp] = idx

    tkeys = sorted(m.keys(),reverse=True)

    for t in tkeys:
        fix_data.append(data[m[t]])
            
    return fix_data

def plot_the_data(data, output_dir, saveAsFileName, plot_title):
   
    each_year = {}
    each_year_m = {}
    each_year_o = {}

    fixDurationList = []
    fixDurationList_m = []
    fixDurationList_o = []

    distList = []
    distList_m = []
    distList_o = []

    # Rearrange by start time
    data = resort(data) 

    for idx,i in enumerate(data):

        typeOfNotice = i['ton']

        start = i['startTime']
        start_ts = python_api.checkTimeFormatReturn(start,'%Y-%m-%d %H:%M')
        if start_ts is None:
            if start.endswith('(All day)'):
                start_ts = fix_if_all_day(start,True)
            else: 
                print 'Wrong time format: ',start
                continue

        # Number of instances for each year
        start_year_str = str(start_ts.year)    

        # Skip if 2007 or 2014
        if start_year_str =='2007' or start_year_str=='2014':
            continue

        increment_map(each_year, start_year_str)
        if typeOfNotice == 'Maintenance':
            increment_map(each_year_m, start_year_str)
        elif typeOfNotice == 'Outage':
            increment_map(each_year_o, start_year_str)
        else: 
            print 'What!', typeOfNotice

        # CDF of distance between each notice
        if idx < len(data)-1:
            # next
            next_i = data[idx+1]
            nx_start = next_i['startTime']
            n_start_ts = python_api.checkTimeFormatReturn(nx_start,'%Y-%m-%d %H:%M')
            if n_start_ts is None:
                if nx_start.endswith('(All day)'):
                    n_start_ts = fix_if_all_day(nx_start,True)
                else: 
                    print 'Wrong time format: ',nx_start
                    continue

            # diff
            tdistance = start_ts - n_start_ts
            if tdistance.total_seconds() < 0:
                 print 'Bogus diff:',start_ts,n_start_ts,idx
                 pass
            elif tdistance.total_seconds() ==0 and start.startswith('2012-03-29 14:'):
#                 print 'Skip 2012/3/29:',start_ts,n_start_ts,idx
                 pass
            else: 
                dist = float(tdistance.total_seconds())/3600.0 #hours
                distList.append(dist)

        # CDF of "duration" 
        end = i['endTime']
        end_ts = python_api.checkTimeFormatReturn(end,'%Y-%m-%d %H:%M')
        if end_ts is None:
            if end.endswith('(All day)'):
                end_ts = fix_if_all_day(end,False)
            else: 
                print 'Wrong time format: ',end
                continue

        tdelta = end_ts - start_ts
        if tdelta.total_seconds() <0:
            print 'Bogus fix time:',end_ts,start_ts,idx
            pass
        elif tdelta.total_seconds() ==0 and end.startswith('2012-03-29 14:'):
#            print 'Skip 0 fix time:',end_ts,start_ts,idx
            pass

        else:
            fixdur = float(tdelta.total_seconds())/ 3600.0  # hours
            fixDurationList.append(fixdur)
            if fixdur > 1000:
                print fixdur
                print i['url']
                print i['startTime']
                print i['endTime']
            if typeOfNotice == 'Maintenance':
                fixDurationList_m.append(fixdur)
            elif typeOfNotice == 'Outage':
                fixDurationList_o.append(fixdur)
            else: 
                print 'What!', typeOfNotice

    ### distance between maintenances
    distList_m = distance_cal('Maintenance',data)

    ### distances between outages
    distList_o = distance_cal('Outage',data)

    # Number of instances for each year
    x_ax = sorted(each_year.keys())
    if x_ax!=sorted(each_year_o.keys()) or x_ax!=sorted(each_year_m.keys()):
        print 'Different x_ax..hmm.....'
        print x_ax
        print sorted(each_year_o.keys())
        print sorted(each_year_m.keys())
        return

    y_map = {}
    y_map['Maintenance'] = []
    y_map['Outage'] = []
    y_map['Total'] = []

    for x in x_ax: # for each year
        y_map['Total'].append(each_year[x]) 
        y_map['Maintenance'].append(each_year_m[x])
        y_map['Outage'].append(each_year_o[x])
    plot_lib.plot_multiline(x_ax, y_map, output_dir, 'eachyear.png', '','Year','Number of notices', (2007,2014),(0,350),5)


    # CDF of distance between each notice
    x_ax, y_tdist = plot_lib.get_cdf2(distList)
    x_ax_m, y_mdist = plot_lib.get_cdf2(distList_m)
    x_ax_o, y_odist = plot_lib.get_cdf2(distList_o)
    plot_lib.plot_multiline_diff([x_ax_m,x_ax_o,x_ax],[y_mdist,y_odist,y_tdist],output_dir,'cdfdist.png','','Distance between notices (hours)', 'CDF', (0,400),(0,1),0)

    # CDF of "duration" 
    x_ax, y_tdur = plot_lib.get_cdf2(fixDurationList)
    x_ax_m, y_mdur = plot_lib.get_cdf2(fixDurationList_m)
    x_ax_o, y_odur = plot_lib.get_cdf2(fixDurationList_o)
    plot_lib.plot_multiline_diff([x_ax_m,x_ax_o,x_ax],[y_mdur,y_odur,y_tdur],output_dir,'cdfdur.png','','Time spent to resolve (hours)', 'CDF', (0,50),(0,1),0)


    return   

def main():

    desc = ( 'Plotting data' )
    usage = ( '%prog [options]\n'
                          '(type %prog -h for details)' )
    op = OptionParser( description=desc, usage=usage )

    # Options
    op.add_option( '--inputfile', '-i', action="store", \
                   dest="input_file", help = "Pickled data")
    
    op.add_option( '--outputdir', '-o', action="store", \
                   dest="output_dir", help = "Directory to store plots")

    # Parsing and processing args
    options, args = op.parse_args()
    args_check = sys.argv[1:]
    if len(args_check) != 4:
        print 'Something wrong with paramenters. Please check.'
        print op.print_help()
        sys.exit(1)

    # Check and add slash to directory if not there.
    output_dir = python_api.check_directory_and_add_slash(options.output_dir)

    # Check file, open, read
    if os.path.isfile(options.input_file) is True:
        fd = open(options.input_file, 'r')
        data = pickle.load(fd)
        fd.close()

    # Plot
    saveAsFileName = ''  # Add file extension yourself.
    plot_title = ''
    plot_the_data(data, output_dir, saveAsFileName, plot_title)


######        
if __name__ == '__main__':
    main()
