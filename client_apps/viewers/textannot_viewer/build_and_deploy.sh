#!/bin/sh
set -e
WEB_ROOT="/var/www/viewers/textannot_viewer"
npm run build
sudo rm -rf $WEB_ROOT
sudo cp -r build/ $WEB_ROOT
sudo /etc/init.d/nginx restart
