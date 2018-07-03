#!/bin/sh
npm run build &&\
sudo rm -rf /var/www/ctwebsite/ &&\
sudo cp -r build/ /var/www/ctwebsite/ &&\
sudo /etc/init.d/nginx restart
