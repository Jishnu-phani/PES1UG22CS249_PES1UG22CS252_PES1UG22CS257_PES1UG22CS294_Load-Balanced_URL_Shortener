#!/bin/bash

# Monitor URL Shortener scaling during stress testing
# This script continuously monitors the status of HPA and pods

echo "Monitoring URL Shortener Kubernetes resources..."
echo "Press Ctrl+C to exit"
echo "--------------------------------------------"

while true; do
    echo -e "\n$(date)"
    echo -e "\n=== Horizontal Pod Autoscaler Status ==="
    kubectl get hpa shortener-hpa -o wide
    
    echo -e "\n=== URL Shortener Pods ==="
    kubectl get pods -l app=shortener -o wide
    
    echo -e "\n=== Pod Resource Usage ==="
    kubectl top pods -l app=shortener
    
    echo -e "\n=== Node Resource Usage ==="
    kubectl top nodes
    
    echo "--------------------------------------------"
    sleep 5
done