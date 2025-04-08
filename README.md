## Docker Instructions

### 1. Build the Docker image

```bash
docker build -t your-dockerhub-username/shortener-app:latest .
```

### 2. Push the image to Docker Hub

```bash
docker login
docker push your-dockerhub-username/shortener-app:latest
```
---

## Kubernetes Deployment Steps

### 1. Start Minikube

```bash
minikube start
```

### 2. Create Redis resources

```bash
kubectl apply -f k8s/redis-pvc.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/redis-service.yaml
```

### 3. Create ConfigMap for the Flask app

```bash
kubectl apply -f k8s/configmap.yaml
```

### 4. Deploy the Flask URL shortener app

```bash
kubectl apply -f k8s/shortener-deployment.yaml
kubectl apply -f k8s/shortener-service.yaml
```

### 5. Deploy the Horizontal Pod Autoscaler (HPA)

```bash
kubectl apply -f k8s/shortener-hpa.yaml
```

### 6. Deploy the Ingress for better traffic routing

```bash
# Enable Ingress addon in Minikube
minikube addons enable ingress

# Apply Ingress configuration
kubectl apply -f k8s/ingress.yaml

# Add host mapping to /etc/hosts (for local testing)
# Replace the IP with your Minikube IP
echo "$(minikube ip) shortener.local" | sudo tee -a /etc/hosts
```
---

## Monitoring & Logs

### View running pods

```bash
kubectl get pods
```

### View logs for a specific pod

```bash
kubectl logs <pod-name>
```

### Tail logs for a pod

```bash
kubectl logs -f <pod-name>
```

### View logs for all shortener pods

```bash
kubectl get pods -l app=shortener -o name | xargs -I {} kubectl logs {}
```

### Tail logs for all shortener pods

```bash
kubectl get pods -l app=shortener -o name | xargs -I {} kubectl logs -f {}
```

### Monitor Horizontal Pod Autoscaler (HPA)

```bash
kubectl get hpa shortener-hpa -o wide --watch
```

### Use the monitoring script to track system scaling

```bash
chmod +x monitor_scaling.sh
./monitor_scaling.sh
```
---

## Access the App (Using Minikube):

### Using NodePort Service

```bash
minikube service shortener-service
```

### Using Ingress (if configured)

Access http://shortener.local in your browser

---

## Stress Testing

Use the provided stress testing script to verify horizontal scaling:

```bash
# Install required packages
pip install requests

# Run the stress test (replace URL with your service URL)
python stress_test.py --url http://shortener.local --threads 20 --requests 10 --duration 120
```

While the stress test is running, monitor the HPA and pod scaling in another terminal with:

```bash
./monitor_scaling.sh
```

You should see the number of pods increase as the load increases, demonstrating the automatic scaling capability.
---

