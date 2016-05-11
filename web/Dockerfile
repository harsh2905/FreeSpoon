FROM ubuntu:14.04.3

MAINTAINER codemeow codemeow@yahoo.com

RUN cp /etc/apt/sources.list /etc/apt/sources.list.raw
ADD https://github.com/codemeow5/software/raw/master/ubt_sources_list_aliyun.txt /etc/apt/sources.list
RUN apt-get update && apt-get install wget -y

RUN apt-get install git -y
RUN apt-get install curl -y
RUN git clone https://github.com/cuilyGitHub/FreeSpoonUI.git
WORKDIR /FreeSpoonUI

RUN curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -
RUN apt-get install nodejs -y
RUN npm install
RUN npm install -g gulp

EXPOSE 80

RUN echo Asia/Shanghai > /etc/timezone && dpkg-reconfigure --frontend noninteractive tzdata

# Dev Tools

RUN apt-get install git -y
RUN apt-get install vim -y

# SSH

RUN apt-get install -y openssh-server
RUN mkdir /var/run/sshd
COPY sshkeys /
RUN cat /sshkeys | chpasswd

RUN sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

EXPOSE 22

# Samba

RUN apt-get install samba -y
COPY smbusers /etc/samba/
COPY smbkeys /
COPY samba.sh /
RUN /bin/bash /samba.sh

EXPOSE 35729

ENTRYPOINT smbd && \
	/usr/sbin/sshd -D
