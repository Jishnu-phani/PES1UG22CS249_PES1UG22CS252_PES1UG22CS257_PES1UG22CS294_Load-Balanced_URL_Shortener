Docker Instructions

1. Build the Docker image

docker build -t your-dockerhub-username/shortener-app:latest .

2. Push the image to Docker Hub

docker login
docker push your-dockerhub-username/shortener-app:latest



⸻

Kubernetes Deployment Steps

1. Create Redis resources

kubectl apply -f k8s/redis-pvc.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/redis-service.yaml

2. Create ConfigMap for the Flask app

kubectl apply -f k8s/configmap.yaml

3. Deploy the Flask URL shortener app

kubectl apply -f k8s/shortener-deployment.yaml
kubectl apply -f k8s/shortener-service.yaml



⸻

Monitoring & Logs

View running pods

kubectl get pods

View logs for a specific pod

kubectl logs <pod-name>

Tail logs for a pod

kubectl logs -f <pod-name>

View logs for all shortener pods

kubectl get pods -l app=shortener -o name | xargs -I {} kubectl logs {}

Tail logs for all shortener pods

kubectl get pods -l app=shortener -o name | xargs -I {} kubectl logs -f {}



⸻

Access the App

For local clusters (like Minikube):

minikube service shortener-service



⸻

