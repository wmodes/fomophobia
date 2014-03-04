#!/bin/bash


cd /usr/local/fomo
tar zcf fomo.tar.gzip . 
date | mail -s "Backup of fomo.tar.gzip" -a fomo.tar.gzip wmodes@gmail.com
