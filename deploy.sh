#!/bin/bash
# deploy.sh — Build Docker images into Minikube and deploy to all namespaces
# Run from the todo-app/ root directory.
# Usage:
#   ./deploy.sh           → deploy all environments
#   ./deploy.sh dev       → deploy only dev
#   ./deploy.sh staging   → deploy only staging
#   ./deploy.sh prod      → deploy only prod

set -e

ENVS=${1:-"dev staging prod"}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🐳  Building images inside Minikube"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Point Docker CLI at Minikube's Docker daemon so images are available in-cluster
eval $(minikube docker-env)

docker build -t todo-frontend:latest ./frontend
echo "✅  todo-frontend:latest built"

docker build -t todo-backend:latest  ./backend
echo "✅  todo-backend:latest built"

# (DB uses the official postgres image — no build needed)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📦  Creating namespaces"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
kubectl apply -f k8s/namespaces.yaml

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀  Deploying environments: $ENVS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for ENV in $ENVS; do
  echo ""
  echo "  ▶  $ENV"
  kubectl apply -k k8s/overlays/$ENV
  echo "  ✅  $ENV deployed"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌐  Access URLs (after pods are Ready)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
MINIKUBE_IP=$(minikube ip)
echo "  dev     →  http://$MINIKUBE_IP:30000"
echo "  staging →  http://$MINIKUBE_IP:30001"
echo "  prod    →  http://$MINIKUBE_IP:30002"

echo ""
echo "  Tip: watch pods across all envs with:"
echo "  kubectl get pods -A -w"
echo ""
