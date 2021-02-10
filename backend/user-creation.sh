#!/bin/bash

username=$1
password=$2
mkdir /backend/clusters/"${username}"
cd /backend/clusters/"${username}"
git clone https://github.com/wtsi-hgi/osdataproc.git
echo "Reaching"
cd osdataproc
pip install -e .
python osdataproc.py create "${username}" --public-key /backend/public_key.pub <<< "${password}"
echo "Done"
