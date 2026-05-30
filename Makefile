.PHONY: install dev test lint clean docker-up docker-down

install:
	pip install -r requirements.txt

dev:
	docker-compose up

test:
	pytest tests/

lint:
	flake8 mcp_server agent backend
	black --check mcp_server agent backend
	isort --check mcp_server agent backend

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

init-db:
	python scripts/init_db.py

seed:
	python scripts/seed_data.py
