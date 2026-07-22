# Makefile
.PHONY: help build run stop clean logs shell test

help:
	@echo "Available commands:"
	@echo "  make build    - Build the Docker image"
	@echo "  make run      - Run the container"
	@echo "  make stop     - Stop the container"
	@echo "  make clean    - Remove container and image"
	@echo "  make logs     - View container logs"
	@echo "  make shell    - Access container shell"
	@echo "  make test     - Test the application"

build:
	docker-compose build

run:
	docker-compose up -d

stop:
	docker-compose down

clean:
	docker-compose down --rmi all -v

logs:
	docker-compose logs -f

shell:
	docker-compose exec streamlit-app /bin/bash

test:
	curl -f http://localhost:8501/_stcore/health && echo "✅ App is healthy"
