# Cluster Launcher

This repository is an extension to the osdataproc project, repo found: https://github.com/wtsi-hgi/osdataproc,
used to bring up hail clusters in an easy, simple web interface. 

# Launching A Cluster:
Creating Hail Clusters has never been easier. In order to create a hail cluster, you will need the following information to hand:
* Your SSH Public Key - An SSH Key can be created using ssh-keygen, if you have one already, this is found in ~/.ssh/id_rsa.pub.
The Number of Workers you wish to have in your cluster
* A Password - This is used to encrypt your volume & is used to connect to the tools associated to osdataproc, e.g. jupyter lab, spark, etc.
* The Tenant you wish to launch in - You will need to contact HGI if it is your first time attempting to launch in a tenant, as you will not be granted access by default
* A Flavour - This is the flavour you want all your instances (Masters & Workers) to have. Prior to launching, you should check the resources in the tenant that you wish to launch in, as launching with too few resources will break your launch. This can be done here: https://metrics.internal.sanger.ac.uk/dashboard/db/fce-available-capacity-theta?refresh=5m&orgId=1 
* Volume Size - The first time you launch a cluster, you will have a volume assigned and created for you. This field allows you to specify the size in Gb. After initial launch, subsequent cluster creations will assume you wish to use the same volume, and will automatically launch using it. If you wish to decouple a volume associated with yourself, contact HGI.

Once all the information has been entered on the site, simply press Launch. The process to load the cluster will take 10-30 Minutes, typically closer to 20-25, depending on connectivity/download speeds of the ansible that osdataproc uses. 


# Using your Cluster:
* Once the cluster is up, refreshing the page will bring you to the Cluster Screen. In this area, you can use the quick hyperlinks to connect to the various services that the cluster offers, Jupyter Lab, Spark, etc. 
* When navigating to these, you will see ‘Your Connection is not Private’. On Chrome, enter “thisisunsafe” into the web browser and it’ll load the appropriate page. On Firefox, click Advanced and ‘Accept Risk and continue’. Once there, you will be asked to enter a username and password to access the resource. The credentials are as follows:
  * The username is: mercury
  * The Password is: What you specified when launching the cluster


# Tearing down your Cluster:
* When the time comes that you no longer need your cluster, you are able to tear it down again (without losing your volume that is mounted to it). To do this, simply click the ‘Destroy Cluster’ Button on the screen. This will cleanly tear down any resources that it brought up, excluding the volume. The Tear-Down process typically takes < 6 Minutes, and once this is done, refreshing will take you to the Cluster Creation Screen where you can create a new cluster at your own discretion.

# What to do in the event of an Error:
* There are a few times when a cluster can break during launch. The main reasons for this would be:
  * A User launching a cluster in a tenant that has too few resources (Security Groups/Security Group Rules/Flavour Availability, etc)
  * Osdataproc/Cluster Launcher losing internet connection and the ansible playbook failing on key launch stages
* In the event of something going wrong during the creation/deletion phase of the cluster, you will be shown an error screen. In the prospect of maintaining stable persistence, once you see an error screen, this will mean that you cannot use/remove your cluster without assistance from a member of the HGI team. Reach out and they should be able to cleanly fix the issue. 
