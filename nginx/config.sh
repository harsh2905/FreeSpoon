#!/bin/bash

sed -i "/yourdomain/s/yourdomain/${NGINX_DOMAIN}/g" /etc/nginx/sites-available/reverse

#DOCKER0=$(ifconfig eth0 | grep inet\ addr | awk '{print $2}' | tr -d "addr:")
#sed -n "/docker0/s/docker0/${DOCKER0}/g" /etc/nginx/sites-available/reverse
