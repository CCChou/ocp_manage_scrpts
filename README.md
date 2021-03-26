# OpenShift Management Scripts
* [Clean Registry Script](https://github.com/CCChou/ocp_management_scripts#clean-registry) : Clean all images in the docker registry
* [Post Install](https://github.com/CCChou/ocp_management_scripts#post-install) : Common post installing steps
* [Configure Infra](https://github.com/CCChou/ocp_management_scripts#configure-infra) : Configure worker node to infra node
* [Configure DNS](https://github.com/CCChou/ocp_management_scripts#configure-dns) : Configure DNS for OpenShift prerequisites
* [Configure LB](https://github.com/CCChou/ocp_management_scripts#configure-lb) : Configure LB for OpenShift prerequisites

## Clean Registry
First, you need to open the delete features in docker registry
```
vim /etc/docker-distribution/registry/config.yml
```

Add storage.delete.enabled = true
```
storage:
    delete:
        enabled: true
```

Restart the registry
```
systemctl restart docker-distribution
```

Run scripts
```
make clean_registry
```

## Post Install

The script will do following things
1. Configure bash completion for OpenShift
2. Add a default user

Run scripts
```
make post_install USER={username} PWD={password}
```

## Configure Infra

Run scripts
```
make configure_infra
```

## Configure DNS

You need to configure the config.json for your environment

Run scripts
```
make configure_dns
```

## Configure LB

You need to configure the config.json for your environment

Run scripts
```
make configure_lb
```

## TODO
* Smoke Test for checking DNS, LB, Internet connection ...etc
* EFK Install
* Service Mesh Install
* Create install_config.yaml
* CoreOS installer automation
