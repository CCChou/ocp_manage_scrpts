import json
import sys
import os
import shutil
from scripts.common.constant import Node


Node = Node()
CONFIG_PATH = '/etc/haproxy/haproxy.cfg'
CONTENT_PATTERN = """
frontend {0}
    bind *:{1}
    default_backend {0}
    mode tcp
    option tcplog

backend {0}
    balance source
    mode tcp
"""

def main():
    if len(sys.argv) < 2:
        print("Usage: configure_lb.py [/path/to/config]")
        return

    config = read_config(sys.argv[1])
    nodes = config['nodes']
    worker_nodes = [node for node in nodes if node['role'] == Node.WORKER or node['role'] == Node.INFRA]
    master_nodes = [node for node in nodes if node['role'] == Node.MASTER or node['role'] == Node.BOOTSTRAP]
    create_config(worker_nodes, master_nodes)
    

def read_config(config_path):
    with open(config_path, 'r') as file:
        return json.load(file)

# Use standard library to create, because you will never know what network environment is.
def create_config(worker_nodes, master_nodes):
    print("Creating the configuration ...")

    content = ''
    content += generate_rule(master_nodes, "openshift-api-server", "6443")
    content += generate_rule(master_nodes, "machine-config-server", "22623")
    content += generate_rule(worker_nodes, "ingress-https", "443")
    content += generate_rule(worker_nodes, "ingress-http", "80")
    
    if os.path.exists(CONFIG_PATH):
        raise('Config already exists')
    shutil.copyfile('./haproxy.cfg.tpl', CONFIG_PATH)
    with open(CONFIG_PATH, 'w') as file:
        file.write(content)

def generate_rule(nodes, name, port):
    content = CONTENT_PATTERN.format(name, port)
    for node in nodes:
        content += '    server {0}    {1}:{2} check\n'.format(node['name'], node['ip'], port)
    return content


if __name__ == '__main__':
    main()
