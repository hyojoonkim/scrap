import sys
import os
import pickle
import re
import operator

THIS_TIMEZONE = 'US/Eastern'
SW_DPID = "00:01:d0:7e:28:cf:5c:f5"     # DPID of switch being tested
CONTROLLER_IP = "15.25.117.134"             # Controller IP
NUM_FLOW_LIST = [400]      # Number of flows to test. By default, it will test 500 flows, one time.


def check_directory_and_add_slash(path):
  return_path = path

  if return_path == None:
    print "None is given. Check given parameter."
    return ''
    
  if os.path.isdir(return_path) is False:
    print "Something wrong in path: '%s'. Abort" % (return_path)
    return ''

  if return_path[-1] != '/':
    return_path = return_path + '/'

  return return_path


def save_data_as_pickle(data, filename, output_dir):
  print '\nSaving Result: %s\n' %(str(filename) + '.p')
  pickle_fd = open(str(output_dir) + str(filename) + '.p','wb')
  pickle.dump(data,pickle_fd)
  pickle_fd.close()

  return


def sort_by_value(the_map):

  # list of tuples (key, value)
  sorted_tup = sorted(the_map.iteritems(), key=operator.itemgetter(1), reverse=True)
  return sorted_tup

    

