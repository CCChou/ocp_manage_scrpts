import json
import sys
import os
import shutil
import subprocess
import glob
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
    configure_haproxy(config)
    

def read_config(config_path):
    with open(config_path, 'r') as file:
        return json.load(file)
    
def configure_haproxy(config):
    subprocess.call("yum -y install haproxy", shell=True)
    create_config(config)
    subprocess.call("systemctl enable haproxy", shell=True)
    subprocess.call("systemctl restart haproxy", shell=True)


# Use standard library to create, because you will never know what network environment is.
def create_config(config):
    print("Creating the configuration ...")

    nodes = config['nodes']
    worker_nodes = [node for node in nodes if node['role'] == Node.WORKER or node['role'] == Node.INFRA]
    master_nodes = [node for node in nodes if node['role'] == Node.MASTER or node['role'] == Node.BOOTSTRAP]

    content = ''
    content += generate_rule(master_nodes, "openshift-api-server", "6443")
    content += generate_rule(master_nodes, "machine-config-server", "22623")
    content += generate_rule(worker_nodes, "ingress-https", "443")
    content += generate_rule(worker_nodes, "ingress-http", "80")
    save_config(content)

def generate_rule(nodes, name, port):
    content = CONTENT_PATTERN.format(name, port)
    for node in nodes:
        content += '    server {0}    {1}:{2} check\n'.format(node['name'], node['ip'], port)
    return content

def save_config(content):
    if os.path.exists(CONFIG_PATH):
        raise FileExistsError('Config already exists')

    template_path = find_filepath('.', 'haproxy.cfg.tpl')
    shutil.copyfile(template_path, CONFIG_PATH)
    with open(CONFIG_PATH, 'w') as file:
        file.write(content)

def find_filepath(path, name):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(name):
                return os.path.join(root, file)
    
    raise FileNotFoundError('Can not find {}'.format(name))

if __name__ == '__main__':
    main()
