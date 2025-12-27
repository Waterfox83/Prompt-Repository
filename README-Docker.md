# Docker Setup for Prompt Repository

This setup runs the entire backend locally using Docker, including a local Qdrant vector database.

## Prerequisites

1. **Docker Desktop** installed and running
2. **AWS Credentials** configured (for S3 access)
3. **Gemini API Key** (for AI-powered generation features)

## Quick Start

### 1. Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your credentials
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - GEMINI_API_KEY
# - S3_BUCKET_NAME
```

### 2. Start the Stack

```bash
# Make the script executable
chmod +x docker-run.sh

# Run it
./docker-run.sh
```

Or manually:

```bash
docker-compose up --build -d
```

### 3. Access Services

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

### 4. Update Frontend Configuration

Point your frontend to the local backend:

```bash
# In frontend directory
export VITE_API_URL=http://localhost:8000
npm run dev
```

Or update `.env` in frontend:
```
VITE_API_URL=http://localhost:8000
```

## Architecture

```
┌─────────────┐
│  Frontend   │ (localhost:5173)
│  (Vite)     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Backend    │ (localhost:8000)
│  (FastAPI)  │
└──────┬──────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌─────────────┐  ┌──────────┐
│     S3      │  │  Qdrant  │ (localhost:6333)
│   (AWS)     │  │  (Local) │
└─────────────┘  └──────────┘
```

## Docker Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Qdrant only
docker-compose logs -f qdrant
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart backend only
docker-compose restart backend
```

### Stop Services
```bash
# Stop but keep data
docker-compose down

# Stop and remove all data
docker-compose down -v
```

### Rebuild After Code Changes
```bash
docker-compose up --build
```

## Configuration

### AWS Credentials

The container needs AWS credentials to access S3. You have two options:

**Option 1: Environment Variables** (in `.env`)
```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_SESSION_TOKEN=your_token  # If using SSO
```

**Option 2: Mount AWS Credentials**
The `docker-compose.yml` already mounts `~/.aws` directory (read-only).

### Qdrant Configuration

- **Local Qdrant**: No API key needed
- **URL**: `http://qdrant:6333` (internal Docker network)
- **Data**: Persisted in Docker volume `qdrant_storage`

### Mock Mode

To run without AWS/Qdrant dependencies:

```env
MOCK_MODE=true
```

This uses in-memory storage with dummy data.

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs backend

# Check if ports are in use
lsof -i :8000
lsof -i :6333
```

### AWS Credentials Not Working
```bash
# Test inside container
docker-compose exec backend aws sts get-caller-identity

# Check environment variables
docker-compose exec backend env | grep AWS
```

### Qdrant Connection Issues
```bash
# Check Qdrant health
curl http://localhost:6333/healthz

# Check collections
curl http://localhost:6333/collections
```

### Clear All Data and Restart
```bash
docker-compose down -v
docker-compose up --build -d
```

## Development Workflow

### 1. Make Code Changes
Edit files in `backend/` directory

### 2. Rebuild Container
```bash
docker-compose up --build -d backend
```

### 3. View Logs
```bash
docker-compose logs -f backend
```

## Production Deployment

For production (Lambda), use the existing build scripts:
```bash
./build_lambda.sh
```

The Docker setup is for **local development only**.

## Data Persistence

- **Qdrant Data**: Stored in Docker volume `qdrant_storage`
- **S3 Data**: Stored in AWS S3 (not affected by Docker)

To backup Qdrant data:
```bash
docker run --rm -v prompt-repository_qdrant_storage:/data -v $(pwd):/backup alpine tar czf /backup/qdrant-backup.tar.gz /data
```

To restore:
```bash
docker run --rm -v prompt-repository_qdrant_storage:/data -v $(pwd):/backup alpine tar xzf /backup/qdrant-backup.tar.gz -C /
```

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `S3_BUCKET_NAME` | AWS S3 bucket name | `llm-prompt-repository` | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | - | Yes (for AI features) |
| `QDRANT_URL` | Qdrant endpoint URL | `http://qdrant:6333` | No (auto-set) |
| `QDRANT_API_KEY` | Qdrant API key | - | No (not needed for local) |
| `MOCK_MODE` | Use in-memory storage | `false` | No |
| `AWS_*` | AWS credentials | - | Yes (for S3) |
