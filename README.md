#Cluster Launcher

This repository is an extension to the osdataproc project, repo found: https://github.com/wtsi-hgi/osdataproc,
used to bring up hail clusters in an easy, simple web interface. The following information is required to bring up
a hail clusters:
 * Your Public Key
 * Desired Flavor for cluster
 * Number of Workers
 * Password for Volume

##Steps for Setup and use:
1. Clone the repo
2. Download a openrc file and move it into the backend directory
3. Ensure Docker is downloaded/usable
4. Run 'docker-compose up --build'
5. The URL for the frontend is: www.localhost:8000
6. Enter the information defined above into the relevant input fields and press the launch cluster button
7. Your Cluster will then be launched
