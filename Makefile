server:
	uv run uvicorn src.server:app --reload
dashboard:
	uv run streamlit run src/dashboard.py

# Build Docker image
docker-build:
	docker build -t milgram-backend .

# Run Docker container locally
docker-run:
	docker run --rm -p 8000:8000 -e PORT=8000 milgram-backend