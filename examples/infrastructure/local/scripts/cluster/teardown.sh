#!/bin/bash
echo "Local cluster tear down requested. This will DELETE ALL applications, services, data, users."
echo "All configurations of the minikube cluster will be removed!" 
echo "WARNING -> Other applications may be affected! <- WARNING"
echo "If you wand to proceed type UNDERSTAND (all caps) below."
read delete_confirmed
if [[ $delete_confirmed = 'UNDERSTAND' ]]
then
  echo "Removing minikube cluster..."
  date # TODO: activate the actual delete  "minikube delete"
  if [[ $? -eq 0 ]]
  then
    echo "Minikube cluster remove completed."
  else
    echo "ERROR: Minikube cluster remove did not complete or executed with errors."
  fi
else
  echo "Delete confirmation missing. Aborting minikube cluster deletion!"
fi
