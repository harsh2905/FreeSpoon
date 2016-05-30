FROM mysql:latest

MAINTAINER codemeow codemeow@yahoo.com

RUN sed -i "/default-character-set/d" /etc/mysql/my.cnf
RUN sed -i "/\[mysqld]/a skip-character-set-client-handshake" /etc/mysql/my.cnf
RUN sed -i "/\[mysqld]/a collation-server=utf8mb4_unicode_ci" /etc/mysql/my.cnf
RUN sed -i "/\[mysqld]/a character-set-server=utf8" /etc/mysql/my.cnf
RUN sed -i "/\[mysqld]/a init_connect= 'SET NAMES utf8mb4' " /etc/mysql/my.cnf
RUN sed -i "/\[mysqld]/a init_connect= 'SET collation_connection = utf8mb4_unicode_ci' " /etc/mysql/my.cnf
RUN sed -i "/\[mysqld]/a max_allowed_packet = '16M' " /etc/mysql/my.cnf
RUN sed -i "/\[mysqld]/a query_cache_size = '16M' " /etc/mysql/my.cnf
RUN sed -i "/\[mysqld]/a query_cache_limit = '1M' " /etc/mysql/my.cnf

RUN echo Asia/Shanghai > /etc/timezone && dpkg-reconfigure --frontend noninteractive tzdata

CMD ["mysqld"]
