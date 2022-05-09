#!/bin/bash
# TODO: Remove the hard coded replica aspect in the abort condition, move db/api keys to secrets
# TODO: For prod the chainlink node must be on DMZ network, oracles run arbitrary HTTP commands!!!
# TODO: Adjust logging level because INFO contains private keys.
source ../../../.env
echo "Generating a ChainLink node ..."
pg_master_pod=$(kubectl get pod -l cluster-name=postgres-server,spilo-role=master -o jsonpath='{.items[0].metadata.name}')
if [ $pg_master_pod = "postgres-server-0" ]
then
  echo "ChainLink postgres server found."
else
  echo "ERROR: No postgres server found!"
  exit 1
fi
echo "Creating configuration ..."
kubectl create -f ./resources/chainlink_node_conf.yaml
if [ $? -eq 0 ]
then
  count=0
  while [ $count -lt 10 ]
  do
    kubectl get configmaps chainlink-node-conf | grep "chainlink-node-conf"
    if [ $? -eq 0 ]
    then
      # Update ConfigMap when it has been loaded
      kubectl patch configmap/chainlink-node-conf --type merge -p '{"data": {"ETH_URL": "wss://rinkeby.infura.io/ws/v3/'$web3_infura_project_id'"}}'
      kubectl patch configmap/chainlink-node-conf --type merge -p '{"data": {"DATABASE_URL": "postgresql://'$pg_user':'$pg_pw'@'$pg_master_pod.postgres-server.default.svc.cluster.local':'$pg_port'/'$chainlink_node_db'?sslmode=require"}}'
      # Files avoid "\n" escaping, cross platform. Alternative "key1"$'\n'"key2" is zsh dependent
      echo $chainlink_node_user >> .tmp
      echo $chainlink_node_pw >> .tmp
      kubectl create secret generic api-env --from-file=.api=.tmp
      rm .tmp
      kubectl create secret generic password-env --from-literal=.password=$chainlink_private_key
      break
    else
      echo "...waiting for kubernetes resource creation..."
      sleep 6
      count=$(( count+1 ))
    fi
  done
else
  echo "ERROR: ChainLink node configuration failed."
fi
sleep 6
kubectl get configmaps chainlink-node-conf | grep "chainlink-node-conf"
if [[ $? -eq 0 ]]
then
  echo "ChainLink node generation completed."
else
  echo "ERROR: ChainLink node generation did not complete or executed with errors."
fi
