#!/bin/bash

username=$1

cd /backend/clusters/"${username}"/osdataproc
python osdataproc.py destroy "${username}" <<< yes

rm -rf /backend/clusters/"${username}"
ls /backend/clusters
