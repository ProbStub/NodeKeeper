#!/bin/bash
echo "Stopping local minikube cluster..."
minikube stop
if [[ $? -eq 0 ]]
then
  echo "Minikube cluster stop completed."
else
  echo "ERROR: Minikube cluster stop did not complete or executed with errors."
fi
