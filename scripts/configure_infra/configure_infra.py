import sys
import json
import subprocess
from scripts.common.constant import Node


Node = Node()

def main():
    if len(sys.argv) < 2:
        print("Usage: configure_infra.py [/path/to/config]")
        return

    config = read_config(sys.argv[1])
    nodes = [node for node in nodes if node['role'] == Node.INFRA]
    configure_infra(nodes)
    configure_router(len(nodes))
    configure_registry()
    configure_monitoring()

def read_config(config_path):
    with open(config_path, 'r') as file:
        return json.load(file)

def configure_infra(nodes):
    for node in nodes:
        subprocess.call("oc label node {} node-role.kubernetes.io/infra=".format(node), shell=True)
        subprocess.call("oc label node {} node-role.kubernetes.io/worker-".format(node), shell=True)

    subprocess.call("oc apply -f ./infra-mcp.yaml", shell=True)
    subprocess.call("oc adm taint nodes -l node-role.kubernetes.io/infra infra=reserved:NoSchedule infra=reserved:NoExecute", shell=True)

def configure_router(nums):
    subprocess.call("oc patch ingresscontroller/default -n  openshift-ingress-operator --type=merge -p \'{\"spec\":{\"nodePlacement\": {\"nodeSelector\": {\"matchLabels\": {\"node-role.kubernetes.io/infra\": \"\"}},\"tolerations\": [{\"effect\":\"NoSchedule\",\"key\": \"infra\",\"value\": \"reserved\"},{\"effect\":\"NoExecute\",\"key\": \"infra\",\"value\": \"reserved\"}]}}}\'", shell=True)
    subprocess.call("oc patch ingresscontroller/default -n openshift-ingress-operator --type=merge -p \'{\"spec\":{\"replicas\": {}}}\'".format(nums), shell=True)

def configure_registry():
    subprocess.call("oc patch configs.imageregistry.operator.openshift.io/cluster --type=merge -p \'{\"spec\":{\"nodeSelector\": {\"node-role.kubernetes.io/infra\": \"\"},\"tolerations\": [{\"effect\":\"NoSchedule\",\"key\": \"infra\",\"value\": \"reserved\"},{\"effect\":\"NoExecute\",\"key\": \"infra\",\"value\": \"reserved\"}]}}\'", shell=True)

def configure_monitoring():
    subprocess.call("oc apply -f ./cluster-monitoring-configmap.yaml", shell=True)


if __name__ == "__main__":
    main()
