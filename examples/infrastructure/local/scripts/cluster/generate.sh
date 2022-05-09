#!/bin/bash
# TODO: add host install needs (minikube, brew, hyperkit go, ipfs-key/ipfs) or utils sidecar pod
# TODO: need to do a minikube tunnel
echo "Generating minikube cluster ..."
# hyperkit is required for ingress-dns to work!
minikube start --driver=hyperkit --memory 8192 --cpus 6 --disk-size 200g
minikube addons enable metrics-server
minikube addons enable ingress
minikube addons enable ingress-dns
echo "A minimal system configuration change is required."
echo "To enable all networking features the domain: simpleservice.test"
echo "must point to the minikube ip address: "$(minikube ip)
echo "Please type your password below if you wish to make the change."

ls /etc/ | grep "resolver"
if [ $? -eq 1 ]
then
  sudo mkdir /etc/resolver
fi
ls /etc/resolver/ | grep "test"
if [ $? -eq 1 ]
then
  local_ip=$(minikube ip)
  sudo -- sh -c "echo 'domain test' >> /etc/resolver/test"
  sudo -- sh -c "echo 'search test' >> /etc/resolver/test"
  sudo -- sh -c "echo 'nameserver '$local_ip >> /etc/resolver/test"
  sudo -- sh -c "echo 'search_order 1' >> /etc/resolver/test"
  sudo -- sh -c "echo 'timeout 5' >> /etc/resolver/test"
  sudo killall -HUP mDNSResponder
else
  echo "Found a test reference in /etc//resolver/ directory"
  echo "No changes have been made. Please check if the configuration is correct!"
fi
minikube status | grep "host: Running"
if [[ $? -eq 0 ]]
then
  echo "Minikube cluster generation completed."
else
  echo "ERROR: Minikube cluster generation did not complete or executed with errors."
fi

