import json
import sys
import subprocess
from abc import ABCMeta, abstractmethod
from scripts.common.constant import Node


Node = Node()
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
    content += 'domain={}.{},{},local\n'.format(cluster_name, base_domain, cidr)
    content += 'server={}\n'.format(upstream)
    return content

def generate_record(nodes, cluster_name, base_domain, lb_ip):
    content = ''
    for node in nodes:
        content += 'host-record={}.{}.{},{}\n'.format(node['name'], cluster_name, base_domain, node['ip'])
    content += 'host-record=api.{}.{},{}\n'.format(cluster_name, base_domain, lb_ip)
    content += 'host-record=api-int.{}.{},{}\n'.format(cluster_name, base_domain, lb_ip)
    content += generate_etcd_record(nodes, cluster_name, base_domain)
    return content

def generate_etcd_record(nodes, cluster_name, base_domain):
    master_nodes = [node for node in nodes if node['role'] == Node.MASTER]
    content = ''
    for i, master_node in enumerate(master_nodes):
        content += 'host-record=etcd-{}.{}.{},{}\n'.format(i, cluster_name, base_domain, master_node['ip'])
    for i in range(3):
        content += 'srv-host=_etcd-server-ssl._tcp.ibm.cp.example,etcd-{}.ibm.cp.example,2380,0,10\n'.format(i)
    return content

def generate_address(nodes, cluster_name, base_domain, lb_ip):
    content = ''
    for node in nodes:
        content += 'address=/{}.{}.{}/{}\n'.format(node['name'], cluster_name, base_domain, node['ip'])
    content += 'address=/apps.{}.{}/{}\n'.format(cluster_name, base_domain, lb_ip)
    content += 'address=/.apps.{}.{}/{}\n'.format(cluster_name, base_domain, lb_ip)
    content += 'address=/api.{}.{}/{}\n'.format(cluster_name, base_domain, lb_ip)
    content += 'address=/api-int.{}.{}/{}\n'.format(cluster_name, base_domain, lb_ip)
    return content

if __name__ == '__main__':
    main()
