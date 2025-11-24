# AI Prompt Repository

A serverless application to store, manage, and search for AI prompts and utilities.

## Architecture
- **Frontend**: React + Vite
- **Backend**: Python FastAPI (AWS Lambda compatible)
- **Storage**: AWS S3
- **Vector DB**: Qdrant + Gemini Embeddings

## 🚀 How to Run Locally

### Prerequisites
1.  **Python 3.12+** and **Node.js 18+** installed.
2.  **AWS Credentials** configured (e.g., `~/.aws/credentials`) with access to the S3 bucket.
3.  **API Keys**:
    - Gemini API Key (Google AI Studio)
    - Qdrant URL & API Key

### 1. Backend Setup
1.  Navigate to the root directory.
2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r backend/requirements.txt
    ```
4.  Set Environment Variables (Mac/Linux):
    ```bash
    export GEMINI_API_KEY="your_gemini_key"
    export QDRANT_URL="your_qdrant_url"
    export QDRANT_API_KEY="your_qdrant_key"
    # export AWS_PROFILE="your_profile" # If not using default
    ```
5.  Run the Server:
    ```bash
    uvicorn backend.main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

### 2. Frontend Setup
1.  Open a new terminal and navigate to `frontend`:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the Dev Server:
    ```bash
    npm run dev
    ```
    The UI will be available at `http://localhost:5173`.

    *Note: The frontend is configured to connect to `http://127.0.0.1:8000` by default when running locally.*

## 📦 Deployment
See [walkthrough.md](walkthrough.md) for deployment instructions.
