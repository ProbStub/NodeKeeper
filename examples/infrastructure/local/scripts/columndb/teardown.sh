#!/bin/bash
source ../../../.env
echo "Postgres tear down requested. This will DELETE ALL views, data, users."
echo "All configurations of the cluster and operator will be removed!"
echo "WARNING -> Other applications may be affected! <- WARNING"
echo "If you wand to proceed type UNDERSTAND (all caps) below."
read delete_confirmed
if [[ $delete_confirmed = 'UNDERSTAND' ]]
then
  kubectl delete -f ./resources/postgres-service.yaml
  count=0
  while [ $count -lt 20 ]
  do
    kubectl get all | grep postgres-server
    if [ $? -eq 1 ]
    then
      echo "Kubernetes cluster removed..."
      break
    else
      echo "...waiting for kubernetes resource removal..."
      sleep 6
      count=$(( count+1 ))
    fi
  done

  kubectl delete -f ./resources/cluster-operator.yaml
fi

kubectl get all | grep postgres
if [[ $? -eq 1 ]]
then
  kill -9 $(pgrep -f $pg_port)
  echo "Postgres removal completed."
else
  echo "ERROR:Postgres removal did not complete or executed with errors."
fi