# Clean Registry

## Usage

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

Restart Docker Distribution
```
systemctl restart docker-distribution
```

Run the clean script
```
python clean_registry.py
```

Reclaim the disk space
```
registry garbage-collect /etc/docker-distribution/registry/config.yml 
```