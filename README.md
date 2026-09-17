# Atlas

## Local Docker deployment

Atlas uses Docker for:

- FastAPI
- Next.js
- PostgreSQL
- Qdrant

Ollama runs natively on macOS to preserve
Apple Silicon Metal acceleration.

### 1. Start Ollama

```bash
ollama serve
ollama pull qwen3:4b
2. Configure Docker environment
cp .env.docker.example .env.docker
3. Build and run
docker compose up -d --build
4. Open Atlas
Frontend:
http://localhost:3000
API docs:
http://localhost:8000/docs

Do not put actual credentials in README.

---

# 71. Add architecture note to README

### File: `README.md`

Also document:

```text
macOS:
Docker API → host.docker.internal → native Ollama

Linux production:
API → configurable external model server