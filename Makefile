export PYTHONPATH:=.:$(PYTHONPATH)
.PHONY: configure_lb

clean_registry:
    python scripts/clean_registry/clean_registry.py
	registry garbage-collect /etc/docker-distribution/registry/config.yml 

post_install:
    sh scripts/post_install/post_install.sh

configure_dns:	
    python scripts/configure_dns/configure_dns.py config.json

configure_lb:
    python scripts/configure_lb/configure_lb.py config.json