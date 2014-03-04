server = "apps.modes.io"
baseurl = "https://apps.modes.io/fomo/fomoserver.py"
user = "fomo"
password = "Ih@t3Twitter"

type = "twitter"

delay_active = 10
delay_inactive = 60
delay_test = 2
delay_bell = 2

# Betabrite configuration

NUL = "\000"
SOH = "\001"
STX = "\002"
ETX = "\003"
EOT = "\004"
ESC = "\033"

ADR = "Z00"         # address: Z=all units, 00=address

#command codes
WRT = "A"           # A=write
WSF = "E"           # F=write special function

FIL = "A"           # filename
POS = "\""          # position: "=bottom

#mode codes
ROT = "a"           # a=rotate
CMP = "t"           # t=rotate compressed
HLD = "b"           # b=hold

# special msg codes
FAS = "\025"        # fastest speed, used in msg
SLO = "\029"        # slowest speed, used in msg
RED = "\034\061"    # change color to red

# special functions
SMC = "$"           # $=set memory configuration
MEM = "AAUFF00FF00" # These bytes mean the following:
                    #    A = File Label
                    #    A = file type (in this case, a STRING file)
                    #    U = an unlocked file
                    #    FF00 = the size of this file in bytes ~64K
                    #    FF = the TEXT file's Start Time (in this case Always)
                    #    00 = the TEXT file's Stop Time (ignored when the Start Time is Always)

# Vorne 87 configuration

EOT2 = "\015"


devalpha = "/dev/ttyAMA0"
alpha = {
    'init': NUL+NUL+NUL+NUL+NUL+SOH+ADR+STX+WSF+SMC+MEM+EOT,
    'display': NUL+NUL+NUL+NUL+NUL+SOH+ADR+STX+WRT+FIL+ESC+POS+CMP+FAS+RED,
    'clear': NUL+NUL+NUL+NUL+NUL+SOH+ADR+STX+WRT+FIL+ESC+POS+HLD+EOT,
    'eot': EOT,
    }

devnum = "/dev/ttyUSB0"
num = {
    'init': SOH+"s:D"+EOT2,
    'display': SOH+"s:D",
    'eot': EOT2,
    }

belldev = "/dev/ttyUSB0"
bell = {
    'init': "",
    'on': SOH+"s:R1"+EOT2,
    'off': SOH+"s:R0"+EOT2,
    }

msgidfile = "fomo.msgid"

logfile = "/var/log/fomo.log"

# serial test
#import serial
#import time
#com = serial.Serial(devnum, 9600, timeout=3)
#com.close() 
#com.open()  
#com.write(bell['on'])
#time.sleep(.125)
#com.write(bell['off'])
#com.close()
