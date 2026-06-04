# Yuki Agent — AI Assistant for Computer Engineering

A FastAPI-based AI agent powered by [Google ADK](https://github.com/google/adk-python) and Gemini, designed as a dandere-style virtual assistant for Computer Engineering students. Deployed on Kubernetes with full CI/CD.

## Overview

Yuki Shiina (椎名 雪) is an AI chatbot assistant serving Computer Engineering students. The backend exposes a REST API that routes user queries through a Google ADK agent using the Gemini 2.5 Flash model, with full session management.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐     ┌────────────┐
│   Frontend   │────▶│  FastAPI API  │────▶│  Google ADK    │────▶│   Gemini   │
│  (separate)  │     │   /ask POST  │     │  Agent Runner  │     │    API     │
└─────────────┘     └──────────────┘     └───────────────┘     └────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   In-Memory   │
                    │   Sessions    │
                    └──────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| API Framework | FastAPI + Uvicorn |
| Agent Framework | Google ADK 2.1+ |
| LLM | Gemini 2.5 Flash |
| Package Manager | uv |
| Containerization | Docker (Python 3.12 Alpine) |
| Orchestration | Kubernetes (k8s) |
| CI/CD | GitHub Actions (GHCR) + Jenkins |
| Ingress | NGINX Ingress Controller |

## Project Structure

```
.
├── api.py                  # FastAPI application — /ask, /health, /ready
├── run.py                  # Agent runner — session setup, query pipeline
├── yuki/
│   ├── agent.py            # Yuki agent definition (system prompt + model)
│   └── .env                # Local environment variables (gitignored)
├── infra/
│   ├── DEPLOYMENT.md       # Kubernetes deployment guide
│   └── k8s/
│       ├── deployment.yaml # Deployment with security context & probes
│       ├── service.yaml    # ClusterIP service
│       ├── ingress.yaml    # NGINX ingress with TLS
│       ├── network-policy.yaml  # Network isolation
│       └── pdb.yaml        # Pod disruption budget
├── .github/workflows/
│   └── build-push-ghcr.yaml  # CI: build & push to GHCR
├── Jenkinsfile             # Alternative CI/CD pipeline
├── Dockerfile              # Multi-stage Alpine-based image
├── pyproject.toml          # Python dependencies (uv)
└── uv.lock                 # Locked dependency versions
```

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Google API key (Gemini access)
- Docker (for containerized deployment)
- Kubernetes cluster + kubectl (for k8s deployment)

## Local Development

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

Create `yuki/.env`:

```env
GOOGLE_API_KEY=your-google-api-key-here
FRONTEND_URL=http://localhost:3001
```

### 3. Run the API server

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Server starts at `http://localhost:8000`.

### 4. Run the agent directly (CLI)

```bash
python run.py
```

## API Reference

### POST /ask

Send a query to the Yuki agent.

**Request:**
```json
{
  "query": "Perkenalkan dirimu"
}
```

**Response:**
```json
{
  "query": "Perkenalkan dirimu",
  "response": "Mm... aku Yuki Shiina..."
}
```

### GET /health

Liveness probe endpoint.

```json
{ "status": "healthy" }
```

### GET /ready

Readiness probe endpoint.

```json
{ "status": "ready" }
```

## Docker

### Build

```bash
docker build -t yuki-agent .
```

### Run

```bash
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your-key \
  -e FRONTEND_URL=http://localhost:3001 \
  yuki-agent
```

## Kubernetes Deployment

See [infra/DEPLOYMENT.md](infra/DEPLOYMENT.md) for the complete deployment guide.

**Quick summary:**

```bash
# 1. Create namespace & secrets
kubectl create namespace yuki
kubectl create secret generic yuki-secrets \
  --from-literal=GOOGLE_API_KEY=your-key \
  --from-literal=FRONTEND_URL=http://localhost:3001 \
  -n yuki

# 2. Apply manifests
kubectl apply -f infra/k8s/

# 3. Verify
kubectl get pods -n yuki
kubectl port-forward svc/yuki-agent 8000:8000 -n yuki
```

### Security

| Feature | Status |
|---------|--------|
| Non-root container | ✓ |
| Read-only filesystem | ✓ |
| Drop all capabilities | ✓ |
| Seccomp profile | ✓ |
| Network policy (ingress + egress) | ✓ |
| TLS ingress | ✓ |
| Pod disruption budget | ✓ |
| Health/readiness probes | ✓ |

### Resources

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 100m | 500m |
| Memory | 128Mi | 512Mi |

## CI/CD

### GitHub Actions

Automatically builds and pushes to GHCR on push to `main`/`master` or `v*` tags.

- **Image**: `ghcr.io/<owner>/<repo>:latest`
- **Tags**: branch, SHA, semver, `latest`
- **Cache**: GitHub Actions cache

### Jenkins

Alternative pipeline via `Jenkinsfile`. Parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `REGISTRY_URL` | `docker.io` | Container registry host |
| `IMAGE_REPOSITORY` | `your-namespace/yuki-agent` | Repository path |
| `REGISTRY_CREDENTIALS_ID` | `docker-registry-credentials` | Credential ID |
| `PUSH_LATEST` | `true` | Also tag as `latest` |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google Gemini API key |
| `FRONTEND_URL` | No | Allowed CORS origin (default: `http://localhost:3001`) |
| `PORT` | No | Server port (Docker default: `8000`) |

## Scaling Considerations

The current deployment uses `InMemorySessionService`. For horizontal scaling:

1. **Session affinity**: Enable sticky sessions in the Service spec.
2. **External session store**: Replace with Redis-backed session persistence for production.

## License

This project is part of a Cloud Computing course assignment (Tugas Akhir / Tubes).
