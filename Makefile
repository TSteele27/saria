.PHONY: default
default: build ;

start: build
	docker-compose -f docker.compose.yml up -d

build:
	docker build .