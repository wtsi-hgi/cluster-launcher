#!/bin/bash

pathToCluster=$1

mkdir "$pathToCluster"
mkdir "$pathToCluster/terraform"
cd $pathToCluster
git clone https://github.com/wtsi-ssg/osdataproc.git
cd ../backend/
