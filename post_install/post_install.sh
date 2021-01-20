#!/bin/bash

if [ $# -ne 2 ] ; then
    echo "Usage: post_install.sh [username] [password]"
    exit 1
fi

TMP_PATH=/tmp/htpasswd
USER=$1
PWD=$2

InstallCompletion() {
    echo "Start installing completion..."

    yum -y install bash-completion
    oc completion bash > /etc/bash_completion.d/oc_completion
    source /usr/share/bash-completion/bash_completion
    source /etc/bash_completion.d/oc_completion
}


AddDefaultUser() {
    echo "Start adding user ..."

    htpasswd -c -B -b $TMP_PATH $USER $PWD
    oc create secret generic htpass-secret --from-file=htpasswd=$TMP_PATH -n openshift-config
    oc apply -f - << EOF
apiVersion: config.openshift.io/v1
kind: OAuth
metadata:
  name: cluster
spec:
  identityProviders:
    - name: my_htpasswd_provider
      mappingMethod: claim
      type: HTPasswd
      htpasswd:
        fileData:
          name: htpass-secret
EOF

    oc adm policy add-cluster-role-to-user cluster-admin $USER
}

InstallCompletion
AddDefaultUser
