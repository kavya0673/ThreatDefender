# ARES - AI-assisted Rapid Evaluation Scanner

ARES is a production-grade Web Application Vulnerability Scanner designed for enterprise security teams. It combines high-speed asynchronous crawling with AI-powered vulnerability analysis.

## Features

- **Intelligent Crawler**: Discovers endpoints, forms, and hidden parameters.
- **Vulnerability Engine**: Detects SQLi, XSS, CSRF, and Misconfigurations.
- **AI Analysis**: Classifies severity and generates human-readable remediation advice.
- **SOC Dashboard**: A premium, futuristic UI for real-time monitoring and reporting.
- **Scalable Architecture**: Built with FastAPI, Celery, and Redis.

## Tech Stack

- **Backend**: Python FastAPI, SQLAlchemy, Celery, Redis
- **Frontend**: React, Tailwind CSS, Lucide Icons
- **Database**: PostgreSQL
- **Infrastructure**: Docker, Docker Compose

## Getting Started

### Prerequisites
- Docker & Docker Compose

### Installation

1. Clone the repository
2. Configure environment variables in `backend/app/core/config.py` (optional: add OpenAI API keys)
3. Run with Docker Compose:

```bash
docker-compose up --build
```

4. Access the Dashboard: `http://localhost:3001`
5. Access the API Docs: `http://localhost:9000/docs`

## Project Structure

```text
├── backend/
│   ├── app/
│   │   ├── api/          # API Endpoints
│   │   ├── core/         # Config & Security
│   │   ├── models/       # DB Models
│   │   ├── scanner/      # Core Engine (Crawler, Modules)
│   │   ├── tasks/        # Celery background tasks
│   │   └── main.py       # Entry point
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/              # React components & styles
│   ├── Dockerfile
│   └── tailwind.config.js
└── docker-compose.yml
```

## Security Disclaimer
This tool is for authorized security testing only. Scanning targets without permission is illegal.
