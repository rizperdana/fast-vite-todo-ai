# Fast Vite Todo AI

A modern boilerplate for building full-stack applications with a Vite-powered frontend and a FastAPI backend. Ideal for rapid prototyping and scalable production projects.

---

## Features

- **Frontend:**
  - Built with [Vite](https://vitejs.dev/) for lightning-fast development
  - Ready for integration with React, Vue, or Svelte (default: React)
  - Hot Module Replacement (HMR)
  - TypeScript support

- **Backend:**
  - Powered by [FastAPI](https://fastapi.tiangolo.com/) for high-performance APIs
  - Async endpoints
  - Automatic OpenAPI/Swagger docs
  - CORS enabled for frontend-backend communication

- **Project Structure:**
  - Clean separation between frontend and backend
  - Easy-to-understand folder organization

---

## Getting Started

### Prerequisites

- Node.js (v18+ recommended)
- Python (3.9+ recommended)
- [Poetry](https://python-poetry.org/) for Python dependency management (optional but recommended)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/rizperdana/fast-vite-todo-ai.git
   cd fast-vite-todo-ai
   ```

2. **Install Frontend dependencies**

   ```bash
   cd frontend
   npm install
   ```

3. **Install Backend dependencies**

   ```bash
   cd ../backend
   # If using Poetry:
   poetry install
   # Or with pip:
   pip install -r requirements.txt
   ```

---

## Development

### Start the Frontend

```bash
cd frontend
npm run dev
```

### Start the Backend

```bash
cd backend
# With Poetry:
poetry run uvicorn main:app --reload
# Or with pip:
uvicorn main:app --reload
```

The frontend will run on [http://localhost:5173](http://localhost:5173) and the backend on [http://localhost:8000](http://localhost:8000).

---

## Customization

- Replace the frontend framework as needed (React, Vue, etc.)
- Add your own API endpoints and business logic in the backend
- Configure environment variables for production

---

## License

MIT © [rizperdana](https://github.com/rizperdana)
