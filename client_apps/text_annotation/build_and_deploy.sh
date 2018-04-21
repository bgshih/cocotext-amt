#!/bin/sh
npm run build &&\
sudo rm -rf /var/www/textannot/ &&\
sudo cp -r build/ /var/www/textannot/ &&\
sudo /etc/init.d/nginx restart
