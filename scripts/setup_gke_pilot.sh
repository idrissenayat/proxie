#!/bin/bash
# walkthrough_gke_setup.sh
# Guide for Pilot Cluster Setup and Domain Configuration

set -e

# Configuration (Change these or set as env vars)
PROJECT_ID="${GCP_PROJECT_ID:-your-gcp-project}"
REGION="${GCP_REGION:-us-central1}"
CLUSTER_NAME="proxie-cluster"
IP_NAME="proxie-static-ip"

echo "===================================================="
echo "   Proxie GKE Pilot Infrastructure Walkthrough"
echo "===================================================="
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"
echo ""

# 1. Enable Required APIs
echo "[1/4] Enabling Google Cloud APIs..."
gcloud services enable \
    container.googleapis.com \
    compute.googleapis.com \
    secretmanager.googleapis.com \
    containerregistry.googleapis.com \
    --project=$PROJECT_ID

# 2. Reserve Global Static IP
echo ""
echo "[2/4] Reserving Global Static External IP..."
echo "This IP will be used for your domain (proxie.app)."
gcloud compute addresses create $IP_NAME \
    --global \
    --project=$PROJECT_ID \
    2>/dev/null || echo "IP already reserved."

STATIC_IP=$(gcloud compute addresses describe $IP_NAME --global --project=$PROJECT_ID --format='value(address)')
echo ">>> STATIC IP: $STATIC_IP"
echo ">>> ACTION REQUIRED: Update your DNS A records for 'proxie.app' and 'api.proxie.app' to point to $STATIC_IP"

# 3. Create GKE Autopilot Cluster
echo ""
echo "[3/4] Creating GKE Autopilot Cluster..."
gcloud container clusters create-auto $CLUSTER_NAME \
    --project=$PROJECT_ID \
    --region=$REGION \
    --release-channel=regular \
    2>/dev/null || echo "Cluster already exists."

# 4. Connect and Apply Manifests
echo ""
echo "[4/4] Connecting to cluster and applying SSL config..."
gcloud container clusters get-credentials $CLUSTER_NAME --project=$PROJECT_ID --region=$REGION

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/ssl.yaml
kubectl apply -f k8s/ingress.yaml

echo ""
echo "===================================================="
echo "   Infrastructure Setup Initiated! "
echo "===================================================="
echo "Progress Checklist:"
echo "1. DNS: Point proxie.app and api.proxie.app -> $STATIC_IP"
echo "2. SSL: Google is provisioning your certs (may take 20-60 mins after DNS propagates)"
echo "3. App: Use '.github/workflows/cd.yml' to push your first deployment."
echo ""
echo "Monitor SSL Status:"
echo "  kubectl describe managedcertificate proxie-ssl-cert -n proxie"
echo ""
echo "Monitor Ingress Status:"
echo "  kubectl get ingress -n proxie"
echo "===================================================="
