# frontend1-react

Lightweight React + Vite frontend for the LLM→Blockdiagram backend.

Features

- Toggle between Text input and PDF upload
- Sends requests to backend endpoints:
  - POST /api/process-text with JSON { text }
  - POST /api/process-pdf as multipart/form-data with file field `file`
- Renders returned Mermaid code using the `mermaid` package

Quick start

1. Install dependencies

```bash
cd frontend1-react
npm install
```

2. Start dev server

```bash
npm run dev
```

3. Open the local dev URL printed by Vite (usually http://localhost:5173) and make sure your Flask backend is running at http://localhost:5000

Notes

- The app expects the backend to return JSON containing `mermaid_code` or `raw_mermaid` string. It follows the same response shape used by the existing back-end endpoints.
- If you prefer to use the existing React app under `frontend/llm-chart-scribe`, you can copy the UI logic from `src/App.jsx` into that project instead.
