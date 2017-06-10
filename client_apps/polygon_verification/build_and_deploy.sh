#!/bin/sh
npm run build &&\
sudo rm -rf /var/www/polyverif/ &&\
sudo cp -r build/ /var/www/polyverif/ &&\
sudo /etc/init.d/nginx restart
