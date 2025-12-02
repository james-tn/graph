# Multi-stage Dockerfile for Contract Intelligence
# Stage 1: Build React Frontend
# Stage 2: Copy GraphRAG data and run FastAPI backend serving both

# ==================== STAGE 1: Build Frontend ====================
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend-build

# Copy frontend package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY frontend/ ./

# Build React app (outputs to dist/)
RUN npm run build

# ==================== STAGE 2: Python Backend + Frontend ====================
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for PostgreSQL, GraphRAG, and Apache AGE
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    curl \
    nodejs \
    npm \
    # Dependencies for Puppeteer/Chromium (mermaid-cli) \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install compatible setuptools for Python 3.12
RUN pip install --no-cache-dir --upgrade pip setuptools>=70.0.0 wheel

# Copy and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ ./backend/

# Install Node.js dependencies for Mermaid validator
# This includes @mermaid-js/mermaid-cli which bundles Puppeteer/Chromium
# The puppeteer-config.json provides --no-sandbox args for Docker
RUN if [ -f backend/utils/package.json ]; then \
    cd backend/utils && npm install --production && npm cache clean --force; \
fi# Copy GraphRAG configuration
COPY graphrag_config/ ./graphrag_config/

# Copy GraphRAG indexed data/output (CRITICAL: This contains the 12,750 entities, 2,909 reports)
# This includes: entities.parquet, relationships.parquet, community_reports.parquet, etc.
COPY data/output/ ./data/output/

# Copy LanceDB vector store
COPY data/output/lancedb/ ./data/output/lancedb/

# Copy built React frontend from stage 1
COPY --from=frontend-builder /frontend-build/dist ./frontend/dist

# Copy any additional data files needed
COPY data/input/ ./data/input/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
# Puppeteer configuration for Docker (no sandbox for containerized environment)
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=false

# Expose port
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI backend (serves both API and static frontend)
# The backend will serve React frontend from /frontend/dist
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
