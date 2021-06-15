#!/bin/bash

username=$1
password=$2
workers=$3
flavor=$4
volume_name=$5
volume_size=$6
lustre_network=$7
lustre_image=$8
network_name="${username}-cluster-network"

mkdir /backend/clusters/"${username}"
cd /backend/clusters/"${username}"
git clone https://github.com/wtsi-hgi/osdataproc.git
cd osdataproc
if [[ $lustre_network == 'None' ]]
then
  if [[ $volume_size -eq 0 ]] || [[ $volume_size == '0' ]]
  then
    python osdataproc.py create "${username}" --nfs-volume $5 --public-key /backend/mercury-key.pub --image-name bionic-server --flavour "${flavor}" --num-workers "${workers}" --network-name "${network_name}" <<< "${password}"
  else
    python osdataproc.py create "${username}" --public-key /backend/mercury-key.pub --nfs-volume $5 --volume-size $6 --image-name bionic-server --flavour "${flavor}" --num-workers "${workers}" --network-name "${network_name}" <<< "${password}"
  fi
else
  if [[ $volume_size -eq 0 ]] || [[ $volume_size == '0' ]]
  then
    python osdataproc.py create "${username}" --public-key /backend/mercury-key.pub --nfs-volume $5 --image-name "${lustre_image}" --flavour "${flavor}" --num-workers "${workers}" --network-name "${network_name}" --lustre-network "${lustre_network}" <<< "${password}"
  else
    python osdataproc.py create "${username}" --public-key /backend/mercury-key.pub --nfs-volume $5 --volume-size $6 --image-name "${lustre_image}" --flavour "${flavor}" --num-workers "${workers}" --network-name "${network_name}" --lustre-network "${lustre_network}" <<< "${password}"
  fi
fi
