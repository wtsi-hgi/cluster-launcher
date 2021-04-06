#!/bin/bash

username=$1
password=$2
workers=$3
flavor=$4
network_name="${username}-cluster-network"

mkdir /backend/clusters/"${username}"
cd /backend/clusters/"${username}"
git clone https://github.com/wtsi-hgi/osdataproc.git
cd osdataproc
#pip install -e .
python osdataproc.py create "${username}" --public-key /backend/mercury-key.pub --flavour "${flavor}" --num-workers "${workers}" --network-name "${network_name}" <<< "${password}"
