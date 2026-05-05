# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from schemas import NotesInput
from rag_engine import process_patient_notes

app = FastAPI(title="Clinic Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "clinic-assistant-api"}


@app.post("/api/structure-notes")
async def structure_notes(data: NotesInput):
    """
    Endpoint to process rough medical notes into structured JSON.
    """
    try:
        if not data.raw_notes.strip():
            raise HTTPException(status_code=422, detail="Patient notes cannot be empty.")

        result = process_patient_notes(data.raw_notes)

        if "error" in result:
            raise HTTPException(status_code=422, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# This allows you to run the file directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
