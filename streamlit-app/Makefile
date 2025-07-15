build:
	docker build -t streamlit-dashboard:latest .

load-image:
	minikube image load streamlit-dashboard:latest

deploy:
	minikube kubectl -- apply -f deployment/streamlit.yaml

