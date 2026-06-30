.PHONY: test run up down build validate
test:
	python -m unittest discover -s tests -v
run:
	python -m app.server
build:
	docker build -t release-radar:local .
up:
	docker compose up --build -d
down:
	docker compose down
validate:
	kubectl kustomize k8s/overlays/prod > /dev/null
	terraform fmt -check -recursive terraform
