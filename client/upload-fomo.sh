#!/bin/bash

if [ ! "$2" ] ; then
    echo "Usage: $0 [TYPE] [IP ADDRESS]"
    echo
    exit 1
fi

target="root@$2"

ssh $target 'mkdir /usr/local/fomo/ &2>1 > /dev/null'
scp config.py.$1 $target:/usr/local/fomo/config.py
scp fomoclient.py fomoclient.init.rc $target:/usr/local/fomo/
ssh $target 'update-rc.d -f fomoclient defaults'
ssh $target 'cd /usr/local/fomo;rm fomo.msgid reallylong.txt config.pyc &2>1 > /dev/null'
ssh $target '/etc/init.d/fomoclient restart'

exit 0

echo "Press Enter to put /etc/rc.d files in place, CTRL-C to stop here""
read var
scp fomoclient.init.rc $target:/etc/init.d/fomoclient
ssh $target 'update-rc.d fomoclient defaults'

echo "Press Enter to REBOOT client machine, CTRL-C to cancel reboot""
echo "After machine comes up, unplug and plug in the USB-to-Serial converter cable"
read var
#ssh $target 'mv /etc/udev/rules.d/40-scratch.rules /usr/local/fomo/'
ssh $target reboot
