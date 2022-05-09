#!/bin/bash
source ../../../.env
echo "ChainLink tear down requested. This will DELETE ALL keys, jobs, users."
echo "All configurations of the node and keys will be removed!"
echo "WARNING -> Ensure wallet key/address are backedup! <- WARNING"
echo "If you wand to proceed type UNDERSTAND (all caps) below."
read delete_confirmed
if [[ $delete_confirmed = 'UNDERSTAND' ]]
# In case of a dropped port forward ...
pg_master_pod=$(kubectl get pod -l cluster-name=postgres-server,spilo-role=master -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward $pg_master_pod $pg_port:$pg_port &
then
  kubectl delete -f resources/chainlink_node.yaml
  count=0
  while [ $count -lt 20 ]
  do
    kubectl get all -l app=chainlink-node-app | grep "deployment.apps/chainlink-node   2/2"
    if [ $? -eq 1 ]
    then
      # remove and drop/recreate db only after the nodes shut down
      kubectl delete -f ./resources/chainlink_node_conf.yaml
      kubectl delete secrets api-env
      kubectl delete secrets password-env
      sleep 4
      psql "postgresql://$pg_user:$pg_pw@$pg_host:$pg_port/postgres" -c "drop database $chainlink_node_db"
      sleep 4
      psql "postgresql://$pg_user:$pg_pw@$pg_host:$pg_port/postgres?sslmode=require" -c "create database $chainlink_node_db with owner=$pg_user"
      echo "Kubernetes cluster removed..."
      break
    else
      echo "...waiting for kubernetes resource removal..."
      sleep 6
      count=$(( count+1 ))
    fi
  done
fi
# After pod removal the chainlink_node db must be dropped and secrets/config map removed!!
kubectl get all -l app=chainlink-node-app | grep "deployment.apps/chainlink-node   2/2"
if [[ $? -eq 1 ]]
then
  kill -9 $(pgrep -f $chainlink_node_port)
  echo "ChainLink removal completed."
else
  echo "ERROR: ChainLink removal did not complete or executed with errors."
fi