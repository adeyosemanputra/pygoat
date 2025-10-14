#!/bin/bash
apt-get -y -qq update

apt-get -y -qq  install software-properties-common # installation of python3 and python3-pip
add-apt-repository ppa:deadsnakes/ppa
apt-get -y -qq update
apt-get -y -qq install python3
apt-get -y -qq install python3-pip # python3 and pip installed

apt-get -y -qq install git # installing git

pip install --require-hashes -r requirements.txt
# or, if it needs dev tools:
# pip install --require-hashes -r requirements-dev.txt
