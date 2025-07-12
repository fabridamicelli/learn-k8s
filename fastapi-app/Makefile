delete-all:
	minikube kubectl delete service postgres-service
	minikube kubectl delete service webapp-service
	minikube kubectl delete -- pod -l app=postgres
	minikube kubectl delete -- pod -l app=webapp
	minikube kubectl delete deployment webapp
	minikube kubectl delete deployment postgres-deployment

build-and-load-app-image:
	docker build -t myapp .
	minikube image load myapp:latest

deploy:
	minikube kubectl -- apply -f postgres-configmap.yaml
	minikube kubectl -- apply -f postgres-secret.yaml
	minikube kubectl -- apply -f postgres.yaml
	minikube kubectl -- apply -f webapp.yaml

