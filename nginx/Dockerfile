FROM ubuntu:14.04.3

MAINTAINER codemeow codemeow@yahoo.com

RUN cp /etc/apt/sources.list /etc/apt/sources.list.raw
ADD https://github.com/codemeow5/software/raw/master/ubt_sources_list_aliyun.txt /etc/apt/sources.list
RUN apt-get update && apt-get install wget -y

RUN apt-get install nginx -y
RUN rm /etc/nginx/sites-enabled/default -f
COPY reverse /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/reverse /etc/nginx/sites-enabled/
#COPY config.sh /
#RUN chmod +x /config.sh
#RUN ./config.sh

EXPOSE 80

RUN echo Asia/Shanghai > /etc/timezone && dpkg-reconfigure --frontend noninteractive tzdata

#CMD ["nginx", "-g", "daemon off;"]

ENTRYPOINT sed -i "/yourdomain/s/yourdomain/${NGINX_DOMAIN}/g" /etc/nginx/sites-available/reverse && \
	/usr/sbin/nginx -g "daemon off;"
