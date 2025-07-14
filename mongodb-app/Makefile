deploy-all:
	minikube kubectl -- apply -f mongo-secret.yaml
	minikube kubectl -- apply -f mongo-configmap.yaml
	minikube kubectl -- apply -f mongo-express.yaml
	minikube kubectl -- apply -f mongo.yaml
	minikube kubectl -- apply -f dashboard-ingress.yaml
