FROM ubuntu:14.04.3

MAINTAINER codemeow codemeow@yahoo.com

RUN cp /etc/apt/sources.list /etc/apt/sources.list.raw
ADD https://github.com/codemeow5/software/raw/master/ubt_sources_list_aliyun.txt /etc/apt/sources.list
RUN apt-get update && apt-get install wget -y

EXPOSE 80

RUN echo Asia/Shanghai > /etc/timezone && dpkg-reconfigure --frontend noninteractive tzdata

RUN apt-get install subversion -y
RUN apt-get install vim -y
RUN apt-get install curl -y
RUN mkdir /WeChatAPI
VOLUME /WeChatAPI

# Dev

RUN apt-get install python-dev python-pip -y
RUN apt-get install redis-server -y
RUN apt-get install mysql-client -y
RUN pip install tornado
RUN pip install BeautifulSoup4
RUN pip install Tornado-MySQL
RUN pip install redis

# Chinese Enviroment

RUN apt-get install locales -y
WORKDIR /usr/share/locales
RUN ./install-language-pack en_US.UTF-8
RUN dpkg-reconfigure locales
RUN export LC_ALL=en_US.UTF-8
RUN echo "export LC_ALL=en_US.UTF-8" >> /etc/bash.bashrc

# SSH

RUN apt-get install -y openssh-server
RUN mkdir /var/run/sshd
COPY sshkeys /
RUN cat /sshkeys | chpasswd

RUN sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]

