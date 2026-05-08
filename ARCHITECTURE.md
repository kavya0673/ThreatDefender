# Enterprise-Grade Security Assessment Platform Architecture

This document outlines the architecture and folder structure for our enterprise website security assessment platform. It leverages a modern, scalable tech stack designed for high performance, reliability, and maintainability.

## 🏗️ Technology Stack

* **Backend:** FastAPI (Python) - *High-performance asynchronous API*
* **Frontend:** React (Vite) - *Fast, modern frontend with modular component architecture*
* **Database:** PostgreSQL - *Relational data storage for users, scans, and reports*
* **Caching & Queue:** Redis - *Fast in-memory datastore for caching and task queue management*
* **Background Tasks:** Celery - *Distributed task queue for running resource-intensive scans asynchronously*
* **Containerization:** Docker & Docker Compose - *Consistent environment across development and production*

## 📂 Folder Structure

### Backend (FastAPI)

The backend follows the standard FastAPI enterprise layout, separating routing, business logic, data models, and schemas.

```text
backend/
├── alembic/                # Database migrations
├── app/
│   ├── api/                # API routers (endpoints)
│   ├── core/               # App configuration, security, events
│   ├── crud/               # Reusable database operations (Create, Read, Update, Delete)
│   ├── db/                 # Database session and connection setup
│   ├── middleware/         # Custom request/response middleware
│   ├── models/             # SQLAlchemy ORM models (Database tables)
│   ├── scanner/            # Core security scanning and AI analysis engines
│   ├── schemas/            # Pydantic models (Data validation & serialization)
│   ├── tasks/              # Celery task definitions (Background jobs)
│   ├── tests/              # Unit and integration tests
│   ├── utils/              # Helper functions and utilities
│   └── main.py             # FastAPI application instance
├── Dockerfile              # Backend container definition
└── requirements.txt        # Python dependencies
```

### Frontend (React + Vite)

The frontend uses a scalable, feature-based architecture to organize components, state, and API integrations.

```text
frontend/
├── public/                 # Static public assets
├── src/
│   ├── assets/             # Images, global icons, fonts
│   ├── components/         # Reusable UI components
│   │   ├── common/         # Buttons, Inputs, Modals, Spinners
│   │   ├── layout/         # Header, Sidebar, Footer
│   │   ├── dashboard/      # Dashboard specific components
│   │   └── scans/          # Scan and report specific components
│   ├── context/            # Global React Contexts (Auth, Theme, AppState)
│   ├── hooks/              # Custom React hooks
│   ├── layouts/            # Page layout wrappers (e.g., AuthLayout, MainLayout)
│   ├── pages/              # Route-level components (Dashboard, Settings, Login)
│   ├── services/           # API clients and external service integrations
│   ├── utils/              # Helper functions, formatters, constants
│   ├── App.jsx             # Main application component & routing
│   └── main.jsx            # Entry point
├── index.html              # Base HTML template
├── package.json            # Node.js dependencies and scripts
├── tailwind.config.js      # TailwindCSS styling configuration
└── vite.config.js          # Vite build configuration
```

### Infrastructure (Docker)

```text
/ (Root)
├── docker-compose.yml      # Orchestrates all services (db, redis, backend, worker, frontend)
├── README.md               # Main project documentation
└── ARCHITECTURE.md         # This architectural overview
```

## 🔄 System Flow

1. **User Request**: The React frontend sends a REST API request to the FastAPI backend.
2. **API Processing**: FastAPI receives the request. If it's a data read, it queries PostgreSQL via SQLAlchemy.
3. **Task Queuing**: If it's a new security scan request, FastAPI publishes a task to Redis and returns a `Task ID` to the client immediately.
4. **Background Execution**: Celery workers pick up the task from Redis, run the deep security analysis (using the `scanner/` modules), and update the database with results.
5. **Real-time Status**: The frontend polls the backend (or uses WebSockets) with the `Task ID` to update the user interface dynamically until the scan is complete.
