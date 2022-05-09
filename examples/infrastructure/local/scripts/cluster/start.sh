#!/bin/bash
echo "Starting local minikube cluster..."
minikube start
if [[ $? -eq 0 ]]
then
  echo "Minikube cluster start completed."
else
  echo "ERROR: Minikube cluster start did not complete or executed with errors."
fi
