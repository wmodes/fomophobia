#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""FOMOphobia is a network-connected installation that immerses the viewer in a visualization of the artist’s real-time social networking anxiety, sounding alarms and keeping count of unhandled content."""
 
__appname__ = "fomofetch.py"
__author__  = "Wes Modes (modes.io)"
__version__ = "0.1pre0"
__license__ = "GNU GPL 3.0 or later"
 
# imports
import config
import logging
import MySQLdb
import poplib
from email import parser
import re
import warnings 
import email.Header
import time
import daemon
from HTMLParser import HTMLParser

# create logger
logger = logging.getLogger(__appname__)
logging.basicConfig(filename=config.logfile,level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
warnings.filterwarnings('ignore')
 
# constants
content_table = "messages"
count_table = "count"

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    try:
        s = MLStripper()
        s.feed(html)
        return s.get_data()
    except HTMLParseError as e:
        logger.exception("HTMLParseError exception: "+str(e))
        return html

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
    for i in range(config.database_retry_attempts):
        logger.info("Attempting to connect to MySQL database")
        try:
            db=MySQLdb.connect(host,user,password,dbname)
            cursor = db.cursor()
            if cursor:
                return db,cursor
        except MySQLdb.Error or MySQLdb.Warning as e:
            logger.exception("Mysql exception: "+str(e))
        logger.info("Waiting for database")
        time.sleep(config.database_recheck_time)
    logger.info("Unable to connect to MySQL after "+database_retry_attempts+" tries")


    # Create table as per requirement
    sql = """CREATE TABLE IF NOT EXISTS messages (
            msgid SERIAL PRIMARY KEY,
            type CHAR(16) NOT NULL,
            fetched TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            message text CHARACTER SET utf8 NOT NULL DEFAULT '')"""
    cursor.execute(sql)

    # Create table as per requirement
    sql = "SHOW TABLES LIKE 'count'"
    cursor.execute(sql)
    result = cursor.fetchone()
    if not result:
        sql = """CREATE TABLE IF NOT EXISTS count (
                type CHAR(16) NOT NULL UNIQUE,
                fetched TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP 
                    ON UPDATE CURRENT_TIMESTAMP,
                count INT NOT NULL DEFAULT 0)"""
        cursor.execute(sql)
        for type in config.types:
            sql = """INSERT INTO count (type, count) VALUES (%s, %s)"""
            cursor.execute(sql, (type, 0))

    # Create table as per requirement
    sql = "SHOW TABLES LIKE 'clients'"
    cursor.execute(sql)
    result = cursor.fetchone()
    if not result:
        sql = """CREATE TABLE IF NOT EXISTS clients (
                type CHAR(16) NOT NULL UNIQUE,
                ip char(24) NOT NULL DEFAULT '0.0.0.0',
                reported TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP 
                    ON UPDATE CURRENT_TIMESTAMP)"""
        cursor.execute(sql)
        for type in config.types:
            sql = """INSERT INTO clients (type) VALUES (%s)"""
            cursor.execute(sql, (type))
    return(db,cursor)


def fetch_warehouse_content(host,port,user,password):
    """Fetch messages from the data warehouse
    Args:
        host: POP3 server
        port: POP3 port
        user: POP3 user
        password: password for POP3 user
    Returns:
        messages
    """
    try:
        Mailbox = poplib.POP3_SSL(host, port)
        #Mailbox.user('recent:'+user)
        Mailbox.user(user)
        #Mailbox.user(user)
        Mailbox.pass_(password)
        messageCount = len(Mailbox.list()[1])
        #messageCount = 3
        # Get messages from server:
        messages = [Mailbox.retr(i) for i in range(1, messageCount + 1)]
        # Close connection to pop server
        Mailbox.quit()
    except poplib.error_proto as e:
        logger.exception("Poplib exception: "+str(e))
        return

    # Concat message pieces:
    messages = ["\n".join(msgParts[1]) for msgParts in messages]
    #Parse message intom an email object:
    messages = [parser.Parser().parsestr(msgParts) for msgParts in messages]
    return messages

def store_content(cursor,messages):
    """Store content in database
    Args:
        messages: a set of mail message objects
    """
    for message in messages:
        type_pattern = "^" + "|^".join(config.types)
        subject, encoding = email.Header.decode_header(message['subject'])[0]
        match = re.search(type_pattern,subject,re.IGNORECASE)
        if match:                      
            type = match.group()
        else:
            type = "unknown"

        if type == "reader":
            type = "rss"
        if type == "gmail":
            type = "email"

        for part in message.walk():
            txtbody = ""
            htmlbody = ""
            if part.get_content_type() == "text/plain":
                txtbody = part.get_payload(decode=True)
            elif part.get_content_type() == "text/html":
                htmlbody = strip_tags(part.get_payload(decode=True))
        if txtbody <> "":
            body = txtbody
        elif htmlbody <> "":
            body = htmlbody
        else:
            body = "No content."

        sql = "INSERT INTO messages(type,message) VALUES(%s, %s)"
        try:
            cursor.execute(sql, (type, body))
            logger.info("Processing "+subject)
            store_count(cursor,type)
        #except mysql_exceptions.OperationalError as e:
        except MySQLdb.OperationalError as e:
            logger.exception("Mysql exception: "+str(e))
            return

def store_count(cursor,type="unknown",count=-1):
    """Store count in database
    Args:
        type (string): describes the type of count
        count (int): the new count (default is -1 indicating it should be incremented by one)
    """
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
    # if the record doesn't exist
    else:
        # create record
        sql = "INSERT INTO count (type,count) VALUES(%s, %s)"
        cursor.execute(sql, (type, count))


def get_count_from_twitter():
    """Get unread message count from Twitter
    Args:
        None
    """ 
def get_count_from_email():
    """Get unread message count from email
    Args:
        None
    """

def get_count_from_rss():
    """Get unread message count from RSS
    Args:
        None
    """

def get_count_from_facebook():
    """Get unread message count from Facebook
    Args:
        None
    """

def get_count_from_sms():
    """Get unread message count from SMS
    Args:
        None
    """

def prune_db(days):
    """Prunes the database of any content older than days_to_prune
    Args:
        days: number of days before which any content should be deleted from db
    Raises:
        IOError: An error occurred accessing the <database>.content object.
    Side Effects:
        Deletes records from the <database>.content table
    """

def run():
    logger.info("starting daemon")
    #options_and_logging()
    #print config.db_host," ",config.db_port," ",config.db_password
    db,cursor=init_db_conx(config.db_host,config.db_port,config.db_user,config.db_password,config.db_name)
    logger.info("Successful database connection")

    while True:
        messages=fetch_warehouse_content(config.pop_host,config.pop_port,config.pop_account,config.pop_password)
        if messages:
            store_content(cursor,messages)
            logger.info("Fetch: ", messages)
        else:
            logger.info("Fetch: No messages")
        time.sleep(config.check_warehouse_delay)


if __name__ == '__main__':

    #with daemon.DaemonContext():
    run()

