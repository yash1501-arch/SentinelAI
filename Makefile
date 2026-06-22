.PHONY: all dev-backend dev-frontend test test-backend test-frontend build-backend build-frontend docker-up docker-down lint clean

all: dev-backend dev-frontend

# Backend
dev-backend:
	@echo "Starting backend..."
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

build-backend:
	cd backend && docker build -t sentinelai-backend .

# Frontend
dev-frontend:
	@echo "Starting frontend..."
	cd frontend && npm run dev

build-frontend:
	cd frontend && npm run build

# Docker
docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

# Tests
test:
	python -m pytest tests/ -v --tb=short

test-backend:
	python -m pytest tests/ -v --tb=short

test-coverage:
	python -m pytest tests/ --cov=backend/app --cov-report=term-missing --cov-report=html

# Lint
lint:
	cd frontend && npm run lint
	cd backend && ruff check app/

# Clean
clean:
	rm -rf backend/app/**/__pycache__ backend/**/*.pyc
	rm -rf frontend/.next frontend/out
	rm -rf .pytest_cache htmlcov .coverage
	rm -rf ml-services/models/*.pkl ml-services/models/*.joblib
