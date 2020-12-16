#!/bin/bash

username=$1
password=$2
mkdir clusters/"${username}"
cd clusters/"${username}"
git clone https://github.com/wtsi-hgi/osdataproc.git
cd osdataproc
python osdataproc.py create "${username}" --public-key /backend/public_key.pub <<< "${password}"
