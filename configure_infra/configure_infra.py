import sys
import subprocess


def main():
    if len(sys.argv) < 2:
        print("Usage: configure_infra.py [node] [node] ...")
        return
    nodes = sys.argv[1:]
    configure_infra(nodes)
    configure_router(len(nodes))
    configure_registry()
    configure_monitoring()

def configure_infra(nodes):
    for node in nodes:
        subprocess.call("oc label node %s node-role.kubernetes.io/infra=" % node, shell=True)
        subprocess.call("oc label node %s node-role.kubernetes.io/worker-" % node, shell=True)

    subprocess.call("oc create -f ./infra-mcp.yaml", shell=True)
    subprocess.call("oc adm taint nodes -l node-role.kubernetes.io/infra infra=reserved:NoSchedule infra=reserved:NoExecute", shell=True)

def configure_router(nums):
    subprocess.call("oc patch ingresscontroller/default -n  openshift-ingress-operator --type=merge -p \'{\"spec\":{\"nodePlacement\": {\"nodeSelector\": {\"matchLabels\": {\"node-role.kubernetes.io/infra\": \"\"}},\"tolerations\": [{\"effect\":\"NoSchedule\",\"key\": \"infra\",\"value\": \"reserved\"},{\"effect\":\"NoExecute\",\"key\": \"infra\",\"value\": \"reserved\"}]}}}\'", shell=True)
    subprocess.call("oc patch ingresscontroller/default -n openshift-ingress-operator --type=merge -p \'{\"spec\":{\"replicas\": %s}}\'" % nums, shell=True)

def configure_registry():
    subprocess.call("oc patch configs.imageregistry.operator.openshift.io/cluster --type=merge -p \'{\"spec\":{\"nodeSelector\": {\"node-role.kubernetes.io/infra\": \"\"},\"tolerations\": [{\"effect\":\"NoSchedule\",\"key\": \"infra\",\"value\": \"reserved\"},{\"effect\":\"NoExecute\",\"key\": \"infra\",\"value\": \"reserved\"}]}}\'", shell=True)

def configure_monitoring():
    subprocess.call("oc create -f ./cluster-monitoring-configmap.yaml", shell=True)


if __name__ == "__main__":
    main()
