SHELL := /bin/bash
.DEFAULT_GOAL := help
.PHONY: up down push help
VERSION := 0.0.1

push: export BUILDX := buildx
push: export FLAGSX := --platform linux/amd64 --push
push: ## Push docker images to registry
	@echo "---> [Building and pushing images]"
	@chmod +x build.sh
	@./build.sh

up: ## Bring up the docker dev stack
	@echo "---> [Building image for local use]"
	@chmod +x build.sh
	@./build.sh
	@echo "---> [Executing docker-compose up]"
	@docker-compose up --detach --remove-orphans
	@docker-compose logs -f

down: ## Bring down the docker dev stack
	@echo "---> [Executing docker-compose down]"
	@docker-compose down -v

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
