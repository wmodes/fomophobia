#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""FOMOphobia is a network-connected installation that immerses the viewer in a visualization of the artist’s real-time social networking anxiety, sounding alarms and keeping count of unhandled content."""
 
__appname__ = "fomoclient.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"
 
# imports
import config
import logging
import re
import warnings 
import time
#import daemon
import requests
import pickle
import urllib2
from requests.auth import HTTPBasicAuth
from os.path import exists
import socket
import serial

import time
import string

logging.basicConfig(filename=config.logfile,level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)
warnings.filterwarnings('ignore')
#logging.captureWarnings(True)

# init things
log = logging.getLogger(__name__)
 
# constants
content_table = "messages"
count_table = "count"
searchMsg = "SEARCHING FOR UNREAD CONTENT"

def options_and_logging():
    """Handle command line options and start logging
    Args:
        None
    """
    from optparse import OptionParser
    parser = OptionParser(version="%%prog v%s" % __version__,
            usage="%prog [options] <argument> ...",
            description=__doc__.replace('\r\n', '\n').split('\n--snip--\n')[0])
    parser.add_option('-v', '--verbose', action="count", dest="verbose",
        default=2, help="Increase the verbosity. Use twice for extra effect")
    parser.add_option('-q', '--quiet', action="count", dest="quiet",
        default=0, help="Decrease the verbosity. Use twice for extra effect")
    #Reminder: %default can be used in help strings.
 
    # Allow pre-formatted descriptions
    parser.formatter.format_description = lambda description: description
 
    opts, args  = parser.parse_args()

    # Set up clean logging to stderr
    log_levels = [logging.CRITICAL, logging.ERROR, logging.WARNING,
                  logging.INFO, logging.DEBUG]
    opts.verbose = min(opts.verbose - opts.quiet, len(log_levels) - 1)
    opts.verbose = max(opts.verbose, 0)
    logging.basicConfig(level=log_levels[opts.verbose],
                        format='%(levelname)s: %(message)s')


def auth_to_server():
    """Authenticate to server
    Args:
        None
    """

def fetch_content(type,msgid,baseurl,user,password):
    """Get content from server
    Args:
        type: content type
        msgid: last msgid retrieved
        baseurl: fomoserver url
        user: htaccess user name
        password: htaccess password
    Returns:
        Returns content string
    """
    payload = {'request': 'content', 'type': type, 'msgid': msgid}
    r = requests.get(baseurl, params=payload, auth=HTTPBasicAuth(user, password), verify=False)
    return r.text.encode('ascii', 'ignore')

def get_count(type,baseurl,user,password):
    """Get count from server
    Args:
        type: content type
        baseurl: fomoserver url
        user: htaccess user name
        password: htaccess password
    Returns:
        Returns count
    """
    payload = {'request': 'count', 'type': type}
    r = requests.get(baseurl, params=payload, auth=HTTPBasicAuth(user, password), verify=False)
    return int(r.text)

def store_msgid(msgid):
    """Store msgid locally
    Args:
        msgid: message id
    Side effect:
        Stores the msgid in a file
    """
    fp = open(config.msgidfile,"wb")
    pickle.dump(msgid, fp)


def get_msgid():
    """Get msgid from local storage
    Args:
        None
    """
    fp = open(config.msgidfile,"rb")
    msgid = pickle.load(fp)
    return msgid

def internet_on():
    try:
        response=urllib2.urlopen('http://74.125.228.100',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False

def server_connected():
    payload = {'request': 'status'}
    if requests.get(config.baseurl, params=payload, auth=HTTPBasicAuth(config.user, config.password), verify=False):
        return True
    return False

def self_test(comA,comN):
    """Go through self-test sequence
    Args:
        com: the serial object of the alpha display
        com: the serial object of the alpha display
    """
    display_number(comN,888)
    display_content(comA,"SELF-TEST")
    time.sleep(config.delay_test)
    display_content(comA,"BELL TEST")
    ring_bell(comN)
    time.sleep(config.delay_test)
    display_content(comA,"CLIENT: "+config.type)
    time.sleep(config.delay_test)
    if internet_on():
        display_content(comA,"INTERNET CONX: OK")
    else:
        display_content(comA,"INTERNET CONX: FAIL")
    time.sleep(config.delay_test)
    if server_connected():
        display_content(comA,"SERVER CONX: OK")
    else:
        display_content(comA,"SERVER CONX: FAIL")
    time.sleep(config.delay_test)
    if report_to_mothership():
        display_content(comA,"PHONE HOME: OK")
    else:
        display_content(comA,"PHONE HOME: FAIL")
    time.sleep(config.delay_test)
    #clear_alpha(comA)
    display_content(comA,searchMsg)

def report_to_mothership():
    """Report current IP and type to fomoserver
    Args:
        None
    """
    # no good, always returns 127.0.1.1
    #ipaddress = socket.gethostbyname(socket.gethostname())
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com",80))
    ipaddress = (s.getsockname()[0])
    s.close()
    payload = {'request': 'report','ip': ipaddress,'type': config.type}
    if requests.get(config.baseurl,params=payload,auth=HTTPBasicAuth(config.user, config.password),verify=False):
        return True
    return False

def display_number(com,count):
    """Display number on the num LED
    Args:
        com: serial object of the display device
        count: the number to display
    """
    print "NUM: ", count
    try:
        if count > 999:
            count = 999
        safenum=str(int(count))
        #com = serial.Serial(config.devnum, 9600, timeout=3)
        #com.close()
        #com.open()
        comstr = config.num['display']+safenum+config.num['eot']
        com.write(comstr)
        #com.close()
    except serial.SerialException as e:
        logging.warning("Serial exception: "+str(e))

def display_content(com,message):
    """Display content on the alpha LED
    Args:
        com: serial object of the display device
        message: the message to display
    """
    #message = message.encode('utf-8')
    #message = message.decode('ascii', 'ignore')
    safeMsg = filter(lambda x: x in string.printable, message)
    safeMsg = safeMsg.replace('\n', ' ')
    print "ALPHA: ", safeMsg
    try:
        #com = serial.Serial(config.devalpha, 9600, timeout=3)
        #com.close()
        #com.open()
        comstr = config.alpha['display'] + safeMsg + config.alpha['eot']
        com.write(comstr)
        #com.close()
    except serial.SerialException as e:
        logging.warning("Serial exception: "+str(e))

def ring_bell(com):
    """Ring the alarm bell
    Args:
        com: serial object of the display device
    """
    print "RING!"
    try:
        #com = serial.Serial(config.devnum, 9600, timeout=3)
        #com.close()
        #com.open()
        com.write(config.bell['on'])
        time.sleep(config.delay_bell)
        com.write(config.bell['off'])
        #com.close()
    except serial.SerialException as e:
        logging.warning("Serial exception: "+str(e))

def clear_alpha(com):
    """Clear the alpha display
    Args:
        None
    Returns:
        Returns a handle to the serial port
    """
    logging.info("Clearing Alpha Display")
    try:
        #com = serial.Serial(config.devalpha, 9600, timeout=3)
        #com.close()
        #com.open()
        com.write(config.alpha['clear'])
        #com.close()
    except serial.SerialException as e:
        logging.warning("Serial exception: "+str(e))
    return com

def init_alpha():
    """Initalize the displays that need it
    Args:
        None
    Returns:
        Returns a handle to the serial port
    """
    logging.info("Initializing Alpha Display")
    try:
        #com = serial.Serial(config.devalpha, 9600, timeout=3)
        com = serial.Serial(config.devalpha, 9600, timeout=None)
        com.close()
        com.open()
        com.write(config.alpha['init'])
        com.write(config.alpha['clear'])
        #com.close()
    except serial.SerialException as e:
        logging.warning("Serial exception: "+str(e))
    return com

def init_num():
    """Initalize the displays that need it
    Args:
        None
    Returns:
        Returns a handle to the serial port
    """
    logging.info("Initializing Number Display")
    try:
        #com = serial.Serial(config.devnum, 9600, timeout=3)
        com = serial.Serial(config.devnum, 9600, timeout=None)
        com.close()
        com.open()
        com.write(config.num['init'])
        #com.close()
    except serial.SerialException as e:
        logging.warning("Serial exception: "+str(e))
    return com

def run():
    logging.info("starting daemon")
    logging.info("starting self-test")
    comN = init_num()
    comA = init_alpha()
    self_test(comA,comN)
    #options_and_logging()

    msgid = 0
    # start by getting the last msgid
    if exists(config.msgidfile):
        msgid=get_msgid()

    while True:
        count = get_count(config.type,config.baseurl,config.user,config.password)
        display_number(comN,count)
        content = fetch_content(config.type,msgid,config.baseurl,config.user,config.password)
        if not re.search("^NO",content,re.IGNORECASE):
            # TODO: Make sure this handles w/out exception the sitch where the input has only one line and can't be split
            msgid,message = content.split('\n', 1)
            logging.info("Fetched msgid "+str(msgid))
            store_msgid(msgid)
            ring_bell(comN)
            display_content(comA,message)
            time.sleep(config.delay_active)
        else:
            logging.info("Inactive: Sleeping for "+str(config.delay_inactive)+" seconds")
            time.sleep(config.delay_inactive)
            display_content(comA,searchMsg)
            #clear_alpha(comA)
            
if __name__ == '__main__':

    #with daemon.DaemonContext():
    run()

