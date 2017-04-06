from secrets import *

warehouse_format = "pop"
pop_host = "pop.gmail.com"
pop_port = 995
pop_account = "fomophobiadata@gmail.com"
db_host = "localhost"
db_port = 3306
db_name = "fomophobia"
db_user = "fomophobia"
types = ["email",
    "gmail",
    "twitter",
    "sms",
    "voicemail",
    "rss",
    "reader",
    "facebook",
    "unknown"]
logfile = "/var/log/fomophobia/fomofetch.log"
check_warehouse_delay = 30
database_recheck_time = 30
database_retry_attempts = 30

print "config file successfully read"
