#!/bin/bash

sed -i "/\[global\]/ausername map = /etc/samba/smbusers" /etc/samba/smb.conf

echo -e "
[FreeSpoon]  
  comment = FreeSpoon
  path = /FreeSpoon
  browseable = yes
  writeable = yes
  guest ok = no
  read only = no
  valid users = root
  admin users = root
  force user = root
  force group = root
" >> /etc/samba/smb.conf

USERNAME=$(cat /smbkeys | cut -d : -f 1)
PASSWORD=$(cat /smbkeys | cut -d : -f 2)

(echo "${PASSWORD}"; echo "${PASSWORD}") | smbpasswd -a ${USERNAME}

pdbedit -L

