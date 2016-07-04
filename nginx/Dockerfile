FROM ubuntu:14.04.3

MAINTAINER codemeow codemeow@yahoo.com

RUN cp /etc/apt/sources.list /etc/apt/sources.list.raw
ADD https://github.com/codemeow5/software/raw/master/ubt_sources_list_aliyun.txt /etc/apt/sources.list
RUN apt-get update && apt-get install wget -y

RUN apt-get install nginx -y
RUN sed -i '/^http {/a\\tclient_max_body_size 10m;' /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/default -f
ADD reverse /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/reverse /etc/nginx/sites-enabled/

EXPOSE 80

RUN echo Asia/Shanghai > /etc/timezone && dpkg-reconfigure --frontend noninteractive tzdata

ENTRYPOINT sed -i "/yourdomain/s/yourdomain/${DOMAINNAME}/g" /etc/nginx/sites-available/reverse && \
	/usr/sbin/nginx -g "daemon off;"
