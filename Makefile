networks:
	docker network create kafka-simple-main || true

up:
	make networks
	docker-compose build --pull
	docker-compose up -d

down:
	docker-compose down

stop:
	make down

logs:
	docker-compose logs -f simple-pub simple-sub another-sub

logs-pub:
	docker-compose logs -f simple-pub

logs-subs:
	docker-compose logs -f simple-sub another-sub

logs-simple-subs:
	docker-compose logs -f simple-sub

up-scale:
	docker-compose up -d --scale simple-pub=50 --scale simple-sub=2

ps:
	docker-compose ps
