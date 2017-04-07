#!/usr/bin/python
# -*- coding: utf-8 -*-
"""FOMOphobia is a network-connected installation that immerses the viewer in a visualization of the artist’s real-time social networking anxiety, sounding alarms and keeping count of unhandled content."""

__appname__ = "fomoserver.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"

# imports
import config
import logging
import MySQLdb
import re
import warnings
import urlparse
#import web
import cgi
#import cgitb; cgitb.enable()  # for troubleshooting

# create logger 
logger = logging.getLogger(__appname__)
logging.basicConfig(filename=config.logfile,level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
warnings.filterwarnings('ignore')

# init things
log = logging.getLogger(__name__)

# constants
content_table = "messages"
count_table = "count"

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


def init_db_conx(host,port,user,password,dbname):
    """Open a connection with the database server
    Args:
        host: database server
        port: database port number
        user: database user
        password: database user password
        database: mysql database
    Raises:
        see _mysql_exceptions
    """
    # connect to database
    db=MySQLdb.connect(host,user,password,dbname)
    cursor = db.cursor()
    #logging.info("Successful database connection")

    # Create table as per requirement
    sql = "SHOW TABLES LIKE 'messages'"
    cursor.execute(sql)
    result = cursor.fetchone()
    if not result:
        logging.info("Table 'messages' absent. Creating.")
        sql = """CREATE TABLE IF NOT EXISTS messages (
                msgid SERIAL PRIMARY KEY,
                type CHAR(16) NOT NULL,
                fetched TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                message text CHARACTER SET utf8 NOT NULL DEFAULT '')"""
        cursor.execute(sql)
        db.commit()

    # Create table as per requirement
    sql = "SHOW TABLES LIKE 'count'"
    cursor.execute(sql)
    result = cursor.fetchone()
    if not result:
        logging.info("Table 'count' absent. Creating.")
        sql = """CREATE TABLE IF NOT EXISTS count (
                type CHAR(16) NOT NULL UNIQUE,
                fetched TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
                count INT NOT NULL DEFAULT 0)"""
        cursor.execute(sql)
        for type in config.types:
            sql = """INSERT INTO count (type, count) VALUES (%s, %s)"""
            cursor.execute(sql, (type, 0))
        db.commit()

    # Create table as per requirement
    sql = "SHOW TABLES LIKE 'clients'"
    cursor.execute(sql)
    result = cursor.fetchone()
    if not result:
        logging.info("Table 'clients' absent. Creating.")
        sql = """CREATE TABLE IF NOT EXISTS clients (
                type CHAR(16) NOT NULL UNIQUE,
                ip char(24) NOT NULL DEFAULT '0.0.0.0',
                reported TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP)"""
        cursor.execute(sql)
        for type in config.types:
            sql = """INSERT INTO clients (type) VALUES (%s)"""
            cursor.execute(sql, (type))
        db.commit()
    return(db,cursor);


def init_web_conx():
    """Initialize web connector
    Args:
        None
    """

def set_unread_count():
    """Set a count manually
    Args:
        None
    """

def reset_unread_count():
    """Set a count to zero
    Args:
        None
    """

def web_authentication():
    """Authenticate to the web server
    Args:
        None
    """

def parse_url_encoding(url):
    """Interpret what is encoded in the URL
    Args:
        url: The full URL to decode
        returns: a list of pairs that make up the query
    """
    parsed_url = urlparse.urlparse(url)
    query = urlparse.parse_qsl(parsed_utl.query)
    return query;

def retrieve_content(dbcursor, msgtype, msgid):
    """Get content from the database
    Args:
        dbcursor: the database cursor object
        type: the type of record
        msgid: the last recrod retrieved
    Returns:
        Returns a string that represents the message body
    """
    sql = "SELECT msgid,message FROM messages WHERE type=%s AND msgid > %s LIMIT 0, 1"
    dbcursor.execute(sql, (msgtype, msgid))
    r = dbcursor.fetchone()
    if r:
        return r;

def serve_content(db, cursor, q):
    """Serve content to requestor
    Args:
        q: query values from url as a dict
        cursor: the database cursor object
    """
    msgtype = q['type']
    msgid = q['msgid']
    logging.info("Retreive content type %s msgid %s" % (msgtype, msgid))
    r = retrieve_content(cursor, msgtype, msgid)
    if r:
       print r[0],"\n",r[1]

    else:
        print "NO RESULTS."

def retrieve_count(cursor,type):
    """Get count from the database
    Args:
        cursor: the database cursor object
        type: the type of record
    """
    sql = "SELECT count FROM count WHERE type=%s"
    try:
        cursor.execute(sql, (type))
        r = cursor.fetchone()
    except:
        pass
    if r:
        return r[0]
    else:
        return 0

def serve_count(db, cursor,q):
    """Serve count to requestor
    Args:
        q: query values from url as a dict
        cursor: the database cursor object
    """
    msgtype = q['type']
    r = retrieve_count(cursor, msgtype)
    if not r:
       r = 0
    print r
    logging.info("Serve count for type %s = %s" % (msgtype, r))

def set_count(db, cursor,q):
    """Set count in the database
    Args:
        q: query values from url as a dict
        cursor: the database cursor object
    """
    type = q['type']
    count = q['count']
    sql = "SELECT count FROM count WHERE type=%s"
    cursor.execute(sql, (type))
    result = cursor.fetchone()
    # if the record exists (as it's supposed to)
    if result:
        # if count not provided, increment the count by one
        if count == -1:
            count = result[0];
            count += 1
        # update record
        sql = "UPDATE count SET count=%s WHERE type=%s"
        cursor.execute(sql, (count,type))
        db.commit()
    # if the record doesn't exist
    else:
        # create record
        sql = "INSERT INTO count (type,count) VALUES(%s, %s)"
        cursor.execute(sql, (type, count))
        db.commit()
    print "OK"

def receive_report(db, cursor,q):
    """Receive report from client and save in database
    Args:
        cursor: the database cursor object
        q: query values from url as a dict
    """
    type = q['type']
    ip = q['ip']
    logging.info("Report received from %s type %s" % (ip, type))
    sql = "SELECT ip FROM clients WHERE type=%s"
    cursor.execute(sql, (type))
    result = cursor.fetchone()
    # if the record doesn't exist (as it's supposed to)
    if not result:
        # create record
        sql = "INSERT INTO clients (type,ip) VALUES(%s, %s)"
        cursor.execute(sql,(type,ip))
        db.commit()
    # if the record exists
    else:
        # update record
        sql = "UPDATE clients SET ip=%s WHERE type=%s"
        cursor.execute(sql,(ip,type))
        db.commit()
    print "OK"

def serve_status(db, cursor):
    """Serve count to requestor
    Args:
        cursor: the database cursor object
    """
    if cursor:
        statusline = "DBCONX: OK  "
    else:
        statusline = "DBCONX: FAIL  "
    print statusline

    print "\nREPORTED BACK TO MOTHERSHIP:"
    sql = "SELECT ip,type,reported FROM clients"
    if not cursor.execute(sql):
        print "No client connections"
    print "\n%15s  %8s  %-19s  %3s" % ("IP Address", "Service",
               "Last Checkin", "Cnt")
    rows = cursor.fetchmany(10)
    for row in rows:
    #while row is not None:
        #print "ROW: ",row
        (ip, msgtype, reported) = row
        count = retrieve_count(cursor, msgtype)
        if ip != '0.0.0.0':
            print "%15s  %8s  %19s  %3i" % (ip, 
                    msgtype, reported, count)
        #row = cursor.fetchone()

def serve_help():
    """Serve count to requestor
    Args:
        cursor: the database cursor object
    """
    print """USAGE:
<baseurl>?request=help
    this help screen
<baseurl>?request=status
    give status of system and report IPs
<baseurl>?request=content&type=<type>&msgid=<lastmsgid>
    request content
<baseurl>?request=count&type=<type>
    request count
<baseurl>?request=set&type=<type>&count=<count>
    set count"""

def encode_data():
    """
    Args:
        None
    """

def main():
    print "Content-type: text/plain"
    print

    #app =  web.application(urls, globals())
    #app.run()
    db,cursor=init_db_conx(config.db_host,config.db_port,config.db_user,config.db_password,config.db_name)

    q = {
        'request': "help",
        'msgid': 0,
        'type': "all",
        'clientid': 0,
        'count': 0
    }

    urlq = cgi.FieldStorage()
    for i in urlq.keys():
        q[i] = urlq[i].value

    #type_pattern = "^" + "|^".join(config.types)

    #print "debug", q

    if q['request'] == "help":
        serve_help()
    elif q['request'] == "content":
        serve_content(db, cursor, q)
    elif q['request'] == "count":
        serve_count(db, cursor, q)
    elif q['request'] == "set":
        set_count(db, cursor, q)
    elif q['request'] == "status":
        serve_status(db, cursor)
    elif q['request'] == "report":
        receive_report(db, cursor, q)

    cursor.close()


if __name__ == "__main__":
    main()
