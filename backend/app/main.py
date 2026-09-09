"""NoteTune HTTP API."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

from .coverage import parse_concepts
from .extraction import ExtractionError, extract_many
from .lyrics import generate_lyrics

load_dotenv()
app = FastAPI(title="NoteTune", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "20")) * 1024 * 1024


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/process")
async def process_notes(files: list[UploadFile] = File(...)) -> dict:
    if not files:
        raise HTTPException(status_code=400, detail="Upload at least one note file.")
    payloads = []
    for upload in files:
        content = await upload.read()
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail=f"{upload.filename} exceeds the upload limit.")
        payloads.append((upload.filename or "notes", content))
    try:
        extracted = extract_many(payloads)
    except ExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    concepts = parse_concepts(extracted)
    lyrics, coverage = generate_lyrics(extracted, concepts)
    return {
        "extracted_text": extracted,
        "concepts": [{"index": item.index, "text": item.text} for item in concepts],
        "lyrics": lyrics,
        "coverage": coverage,
    }


@app.post("/api/process.txt", response_class=PlainTextResponse)
async def process_notes_as_text(files: list[UploadFile] = File(...)) -> str:
    result = await process_notes(files)
    return result["lyrics"]
