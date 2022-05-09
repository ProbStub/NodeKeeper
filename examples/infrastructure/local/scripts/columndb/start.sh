#!/bin/bash
source ../../../.env
echo "Starting postgres service..."
# Note that for cluster name must match {TEAM}-{NAME} format; TEAM=postgres, NAME=server!!!!
kubectl apply -f ./resources/postgres-service.yaml
count=0
while [ $count -lt 30 ]
do
  kubectl get all -l team=postgres | grep "statefulset.apps/postgres-server   3/3"
  if [ $? -eq 0 ]
  then
    break
  else
    echo "...waiting for kubernetes resource creation..."
    sleep 6
    count=$(( count+1 ))
  fi
done
kubectl get all -l team=postgres | grep "statefulset.apps/postgres-server   3/3"
if [[ $? -eq 0 ]]
then
  # PG Operator replaces underscores for secret storage in K8
  pg_user_secret=$(echo $pg_user | sed "s/_/-/")
  pg_pw=$(kubectl get secret $pg_user_secret.postgres-server.credentials.postgresql.acid.zalan.do -o 'jsonpath={.data.password}' | base64 -d)
  sed -i -e 's/pg_pw.*/pg_pw="'$pg_pw'"/g' ../../../.env
  pg_master_pod=$(kubectl get pod -l cluster-name=postgres-server,spilo-role=master -o jsonpath='{.items[0].metadata.name}')
  kill -9 $(pgrep -f $pg_port)
  kubectl port-forward $pg_master_pod $pg_port:$pg_port &
  echo "Postgres service start completed."
else
  echo "ERROR: Postgres service start did not complete or executed with errors."
fi
