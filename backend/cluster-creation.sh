#!/bin/bash

username=$1
password=$2
workers=$3
flavor=$4
volume_name=$5
volume_size=$6
network_name="${username}-cluster-network"

mkdir /backend/clusters/"${username}"
cd /backend/clusters/"${username}"
git clone https://github.com/wtsi-hgi/osdataproc.git
cd osdataproc
if [[ $volume_size -eq 0 ]] || [[ $volume_size == '0' ]]
then
  echo $volume_size
  echo $volume_name
  python osdataproc.py create "${username}" --nfs-volume $5 --public-key /backend/mercury-key.pub --image-name bionic-server --flavour "${flavor}" --num-workers "${workers}" --network-name "${network_name}" <<< "${password}"
else
  echo $volume_size
  echo $volume_name
  python osdataproc.py create "${username}" --public-key /backend/mercury-key.pub --nfs-volume $5 --volume-size $6 --image-name bionic-server --flavour "${flavor}" --num-workers "${workers}" --network-name "${network_name}" <<< "${password}"
fi
