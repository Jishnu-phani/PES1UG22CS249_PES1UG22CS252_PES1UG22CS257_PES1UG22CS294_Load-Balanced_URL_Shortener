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
---

## Access the App (Using Minikube):

```bash
minikube service shortener-service
```
---

