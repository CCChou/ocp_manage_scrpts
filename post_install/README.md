# Post Install

## Goals
* Configure the OpenShift bash completion
* Create a cluster-admin user to replace kubeadmin

## Prerequisite

1. Login OpenShift with cluster-admin user
```
oc login -u [user] -p [password]
```

2. Make sure you have the repository enabled


## Usage

You need to give the script user and password information for creating the account
```
post_install.sh [username] [password]
```
