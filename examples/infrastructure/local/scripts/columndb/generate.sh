#!/bin/bash
echo "Generating Postgres cluster operator ..."
kubectl apply -f ./resources/cluster-operator.yaml
count=0
while [ $count -lt 10 ]
do
  kubectl get pod -l name=postgres-operator | egrep "^postgres-operator-[[:alnum:]]{10}-[[:alnum:]]{5}[[:space:]]{3}1\/1"
  if [ $? -eq 0 ]
  then
    break
  else
    echo "...waiting for kubernetes resource creation..."
    sleep 6
    count=$(( count+1 ))
  fi
done
kubectl get pod -l name=postgres-operator | egrep "^postgres-operator-[[:alnum:]]{10}-[[:alnum:]]{5}[[:space:]]{3}1\/1"
if [[ $? -eq 0 ]]
then
  echo "Postgres cluster operator generation completed."
else
  echo "ERROR: Postgres cluster operator generation did not complete or executed with errors."
fi
