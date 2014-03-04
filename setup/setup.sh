LOCAL="~wmodes/dev/fomo"

mkdir  /var/www/fomo
ln -s $LOCAL/fomofetch/fomofetch.py /usr/local/bin/
ln -s $LOCAL/fomofetch/config.py /etc/fomofetch.conf

ln -s $LOCAL/setup/fomo.conf /etc/httpd/conf.d/
ln -s $LOCAL/fomoserver/fomoserver.py /var/www/fomo/
ln -s $LOCAL/fomoserver/htpasswd /etc/fomopasswd
