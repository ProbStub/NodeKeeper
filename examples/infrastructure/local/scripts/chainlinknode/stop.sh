#!/bin/bash
source ../../../.env
echo "Stopping ChainLink node..."
kubectl delete -f resources/chainlink_node.yaml
if [[ $? -eq 0 ]]
then
  kill -9 $(pgrep -f $chainlink_node_port)
  echo "ChainLink node stop completed. Stopping only removes pod compute resources!"
else
  echo "ERROR: ChainLink node stop did not complete or executed with errors."
fi
