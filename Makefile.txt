.PHONY: install run clean test

install:
	@bash scripts/install.sh

run:
	@python3 run.py

test:
	@pytest tests/ -v

clean:
	@rm -rf __pycache__ app/__pycache__ .pytest_cache
	@rm -f ~/.cpu-web-tuner/logs/*.jsonl

docker-build:
	@cd docker && docker build -t cpu-web-tuner .

docker-run:
	@cd docker && docker-compose up

service-start:
	@sudo systemctl start cpu-web-tuner

service-stop:
	@sudo systemctl stop cpu-web-tuner

service-status:
	@sudo systemctl status cpu-web-tuner