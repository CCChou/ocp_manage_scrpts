import json
import sys
import subprocess
from abc import ABCMeta, abstractmethod


MASTER = 'master'
CONFIG_PATH = '/etc/dnsmasq.d/dns.conf'

def main():
    if len(sys.argv) < 2:
        print("Usage: configure_dns.py [/path/to/config]")
        return

    config = read_config(sys.argv[1])
    configure_dnsmasq(config)

def read_config(config_path):
    with open(config_path, 'r') as file:
        return json.load(file)

def configure_dnsmasq(config):
    subprocess.call("yum -y install dnsmasq", shell=True)
    create_config(config)
    subprocess.call("systemctl enable dnsmasq", shell=True)
    subprocess.call("systemctl restart dnsmasq", shell=True)

# Use standard library to create, because you will never know what network environment is.
def create_config(config):
    print("Creating the configuration ...")

    content = generate_config_content(config)
    with open(CONFIG_PATH, 'w') as file:
        file.write(content)

def generate_config_content(config):
    cluster_name = config['clusterName']
    base_domain = config['baseDomain']
    lb_ip = config['lb']
    cidr = config['cidr']
    upstream = config['upstream']
    nodes = config['nodes']
    
    content = ''
    content += generate_base(cluster_name, base_domain, cidr, upstream)
    content += generate_record(nodes, cluster_name, base_domain, lb_ip)
    content += generate_address(nodes, cluster_name, base_domain, lb_ip)
    return content

def generate_base(cluster_name, base_domain, cidr, upstream):
    content = ''
    content += 'domain=%s.%s,%s,local\n' % (cluster_name, base_domain, cidr)
    content += 'server=%s\n' % upstream
    return content

def generate_record(nodes, cluster_name, base_domain, lb_ip):
    master_nodes = [node for node in nodes if node['role'] == MASTER]
    content = ''
    for node in nodes:
        content += 'host-record=%s.%s.%s,%s\n' % (node['name'], cluster_name, base_domain, node['ip'])
    content += 'host-record=api.%s.%s,%s\n' % (cluster_name, base_domain, lb_ip)
    content += 'host-record=api-int.%s.%s,%s\n' % (cluster_name, base_domain, lb_ip)

    for i, master_node in enumerate(master_nodes):
        content += 'host-record=etcd-%s.%s.%s,%s\n' % (i, cluster_name, base_domain, master_node['ip'])

    for i in range(3):
        content += 'srv-host=_etcd-server-ssl._tcp.ibm.cp.example,etcd-%s.ibm.cp.example,2380,0,10\n' % i

    return content

def generate_address(nodes, cluster_name, base_domain, lb_ip):
    content = ''
    for node in nodes:
        content += 'address=/%s.%s.%s/%s\n' % (node['name'], cluster_name, base_domain, node['ip'])
    content += 'address=/apps.%s.%s/%s\n' % (cluster_name, base_domain, lb_ip)
    content += 'address=/.apps.%s.%s/%s\n' % (cluster_name, base_domain, lb_ip)
    content += 'address=/api.%s.%s/%s\n' % (cluster_name, base_domain, lb_ip)
    content += 'address=/api-int.%s.%s/%s\n' % (cluster_name, base_domain, lb_ip)
    return content

if __name__ == '__main__':
    main()
