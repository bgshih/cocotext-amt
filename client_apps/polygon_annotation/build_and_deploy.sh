#!/bin/sh
npm run build &&\
sudo rm -rf /var/www/polyannot/ &&\
sudo cp -r build/ /var/www/polyannot/ &&\
sudo /etc/init.d/nginx restart
