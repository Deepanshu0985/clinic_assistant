# Clinic Assistant - Medical Documentation Helper

Clinic Assistant is a local full-stack RAG application for helping clinic staff turn rough patient notes into structured documentation. It extracts key details, creates a concise visit summary, and flags missing documentation fields.

This is not a diagnostic tool. It is intended only for documentation support and information structuring.

## Tech Stack

- Backend: Python, FastAPI
- Frontend: React, Vite
- Local LLM: Ollama with `mistral:7b`
- Embeddings: Ollama with `nomic-embed-text`
- RAG framework: LangChain
- Vector store: ChromaDB

## Project Structure

```text
clinic-assistant/
  backend/
    data/               # Sample medical reference documents
    chroma_db/          # Local Chroma vector store
    main.py             # FastAPI app and REST endpoints
    rag_engine.py       # Document loading, chunking, retrieval, LLM chain
    prompt.py           # Documentation-focused prompt
    schemas.py          # Request validation
    requirements.txt
  frontend/
    src/
      App.jsx           # Main UI
      App.css
    package.json
```

## Prerequisites

Install Ollama from:

```text
https://ollama.com/
```

Pull the local models:

```bash
ollama pull mistral:7b
ollama pull nomic-embed-text
```

Make sure Ollama is running before starting the backend.

## Backend Setup

From the project root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Build or refresh the local ChromaDB vector store from the sample reference documents:

```bash
python rag_engine.py
```

Start the FastAPI server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Main API endpoint:

```bash
curl -X POST http://localhost:8000/api/structure-notes \
  -H "Content-Type: application/json" \
  -d '{"raw_notes":"John Doe, 45, cough and SOB for 3 days. BP 130/85. Takes albuterol. NKDA."}'
```

## Frontend Setup

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open the Vite URL shown in the terminal, usually:

```text
http://localhost:5173
```

The frontend sends requests to:

```text
http://localhost:8000/api/structure-notes
```

## Knowledge Base

The sample knowledge base lives in `backend/data/` and includes:

- `soap_template.txt`
- `required_intake_fields.txt`
- `medical_abbreviations.txt`
- `patient_intake_checklist.txt`
- `medication_allergy_documentation.txt`

The backend loads these text files, splits them into chunks using LangChain's `RecursiveCharacterTextSplitter`, embeds the chunks with `nomic-embed-text`, and stores them in ChromaDB. At request time, the app retrieves the top matching chunks and passes them to the local LLM as context.

Current chunking settings are in `backend/config.py`:

```python
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
```

## API Response Shape

The LLM is prompted to return only JSON with this structure:

```json
{
  "structured_summary": "Professional visit summary.",
  "extracted_details": {
    "Patient Name": "John Doe",
    "Age": 45,
    "Symptoms": ["cough", "shortness of breath"],
    "Medications": ["albuterol"]
  },
  "missing_fields": ["date of birth", "assessment", "plan"]
}
```

## Design Decisions and Trade-Offs

I used FastAPI because it is lightweight, easy to validate with Pydantic, and simple to expose as a REST API for the React frontend. LangChain and ChromaDB keep the RAG pipeline small enough for a take-home prototype while still showing the full flow: load reference documents, chunk them, embed them, retrieve relevant guidance, and pass that context into a local Ollama model. I chose `mistral:7b` as the default LLM because it is capable enough for structured extraction while remaining practical for local machines. The main trade-off is that local model output can still occasionally produce invalid JSON or miss details, so the backend validates empty input and returns a clear error if the LLM response cannot be parsed. This prototype prioritizes explainability and local execution over production-grade reliability.

## Error Handling

- Empty or whitespace-only notes are rejected.
- If the LLM returns invalid JSON, the API returns a validation error.
- The frontend shows loading and error states.
- Missing documentation fields are flagged instead of guessed.

## Notes for Evaluation

- No paid APIs are used.
- All LLM and embedding calls run locally through Ollama.
- The app is for documentation support only and does not make clinical decisions.
