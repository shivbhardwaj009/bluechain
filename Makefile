.PHONY: install test run-backend run-frontend train clean docker-up docker-down

install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

test:
	pytest backend/tests -v

run-backend:
	python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

train:
	python ml/training/train_sst_forecaster.py

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f bluechain.db
