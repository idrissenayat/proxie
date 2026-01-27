#!/bin/bash
# Proxie Kubernetes Deployment Script

set -e

PROJECT_ID="${GCP_PROJECT_ID:-your-gcp-project}"
REGION="${GCP_REGION:-us-central1}"
CLUSTER_NAME="proxie-cluster"

echo "=== Proxie Kubernetes Deployment ==="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Step 1: Create GKE Autopilot Cluster (if not exists)
echo "Creating GKE Autopilot cluster..."
gcloud container clusters create-auto $CLUSTER_NAME \
  --project=$PROJECT_ID \
  --region=$REGION \
  --release-channel=regular \
  2>/dev/null || echo "Cluster already exists"

# Step 2: Get credentials
echo "Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME \
  --project=$PROJECT_ID \
  --region=$REGION

# Step 3: Install Kong Ingress Controller
echo "Installing Kong Ingress Controller..."
kubectl apply -f https://raw.githubusercontent.com/Kong/kubernetes-ingress-controller/main/deploy/single/all-in-one-dbless.yaml \
  2>/dev/null || echo "Kong already installed"

# Step 4: Build and push Docker images
echo "Building and pushing Docker images..."
docker build -t gcr.io/$PROJECT_ID/proxie-api:latest .
docker push gcr.io/$PROJECT_ID/proxie-api:latest

cd web-next
docker build -t gcr.io/$PROJECT_ID/proxie-web:latest .
docker push gcr.io/$PROJECT_ID/proxie-web:latest
cd ..

# Step 5: Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."

# Update PROJECT_ID in manifests
sed -i.bak "s/PROJECT_ID/$PROJECT_ID/g" k8s/*.yaml

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml  # Ensure real secrets are created
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/postgres-statefulset.yaml

echo "Waiting for database..."
kubectl wait --for=condition=ready pod -l app=postgres -n proxie --timeout=120s

kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/worker-deployment.yaml
kubectl apply -f k8s/web-deployment.yaml
kubectl apply -f k8s/ingress.yaml

echo "=== Deployment Complete ==="
echo ""
echo "Check status:"
echo "  kubectl get pods -n proxie"
echo ""
echo "Get external IP:"
echo "  kubectl get ingress -n proxie"
