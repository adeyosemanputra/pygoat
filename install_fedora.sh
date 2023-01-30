#!/bin/bash
echo "INSTALL DEPENDENCIES"

yum -y install libpq-devel
yum -y install zlib-devel
yum -y install libjpeg-devel
yum -y install libffi-devel
yum -y install python3-devel

echo "ADDING FIREWALLD RULES FOR PORT 8000"
firewall-cmd  --add-port=8000/tcp --permanent
firewall-cmd --reload