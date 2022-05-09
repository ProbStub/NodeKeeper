#!/bin/bash
source ../../../.env
echo "Starting ChainLink node..."
kubectl apply -f resources/chainlink_node.yaml
count=0
while [ $count -lt 5 ]
do
  kubectl get all -l app=chainlink-node-app | grep "deployment.apps/chainlink-node   2/2"
  if [ $? -eq 0 ]
  then
    kill -9 $(pgrep -f $chainlink_node_port)
    kubectl port-forward service/chainlink-node-service $chainlink_node_port:$chainlink_node_port &
    sleep 2
    index=0
    while [ $index -lt 30 ]
    do
      curl http://localhost:6688 | grep "Chainlink"
      if [ $? -eq 0 ]
      then
curl --cookie-jar cookie.txt -X POST -H "Content-Type: application/json" \
http://localhost:6688/sessions -d '{"email":"'$chainlink_node_user'", '\
'"password":"'$chainlink_node_pw'"}'

node_accounts=$(curl --cookie cookie.txt -X POST -H "Content-Type: application/json" \
http://localhost:6688/query -d '{"operationName":"FetchETHKeys","variables":{},"query": '\
'"fragment ETHKeysPayload_ResultsFields on EthKey {\n  address\n  chain {\n    id\n'\
'__typename\n  }\n  createdAt\n  ethBalance\n  isFunding\n  linkBalance\n  __typename\n}'\
'\n\nquery FetchETHKeys {\n  ethKeys {\n    results {\n      ...ETHKeysPayload_ResultsFields\n'\
'      __typename\n    }\n    __typename\n  }\n}\n"}')

chain_link_node_wallet_address=$(echo $node_accounts| jq -r '.data.ethKeys.results[0].address')

sed -i -e 's/chain_link_node_wallet_address.*/chain_link_node_wallet_address="'\
$chain_link_node_wallet_address'"/g' ../../../.env
rm cookie.txt
rm ../../../.env-e

        echo "ChainLink node start completed."
        exit 0
      else
        echo "...retrying pod creation..."
        kubectl delete pods -l app=chainlink-node-app
        sleep 3
        kubectl delete -f  resources/chainlink_service.yaml
        kubectl apply -f  resources/chainlink_service.yaml
        kill -9 $(pgrep -f $chainlink_node_port)
        kubectl port-forward service/chainlink-node-service $chainlink_node_port:$chainlink_node_port&
        sleep 2
        index=$(( $index+1 ))
      fi
    done
  else
    echo "...waiting for kubernetes resource creation..."
    sleep 6
    count=$(( count+1 ))
  fi
done
echo "ERROR: ChainLink node start did not complete or executed with errors."

