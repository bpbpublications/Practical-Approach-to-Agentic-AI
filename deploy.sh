#!/bin/bash

echo "Building Docker image for Chainlit App..."
# eval $(minikube docker-env) #uncomment this if using minikube
docker build -t chainlit-app .

echo "Deploying Chainlit App to Kubernetes..."

echo "Deleting existing resources..."
kubectl delete hpa chainlit-app-hpa
kubectl delete deployment chainlit-app
kubectl delete service chainlit-service

echo "Applying new resources..."
kubectl apply -f ./src/Chapter11/k8s/chainlit-app-deployment.yaml
kubectl apply -f ./src/Chapter11/k8s/chainlit-app-service.yaml
kubectl apply -f ./src/Chapter11/k8s/chainlit-app-hpa.yaml

echo "Deployment complete."