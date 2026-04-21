import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from .services.text_cleaner import clean_text

from .database import Base, engine, get_db
from . import crud, models, schemas
from .services.file_parser import extract_text_from_pdf, extract_text_from_txt
from .services.summarizer import summarize_text
from .services.keywords import extract_keywords
from .services.quiz_generator import generate_quiz_questions

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "app/storage/uploads")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

os.makedirs(UPLOAD_DIR, exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Lecture Summarizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/upload", response_model=schemas.LectureOut)
async def upload_lecture(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = file.filename.lower().split(".")[-1]
    if ext not in ["pdf", "txt"]:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported.")

    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if ext == "pdf":
        raw_text = extract_text_from_pdf(save_path)
    else:
        raw_text = extract_text_from_txt(save_path)
    
    raw_text = clean_text(raw_text)

    if not raw_text:
        raise HTTPException(status_code=400, detail="Could not extract text from file.")

    lecture = crud.create_lecture(db, filename=file.filename, filepath=save_path, raw_text=raw_text)
    return schemas.LectureOut(
        id=lecture.id,
        filename=lecture.filename,
        raw_text_preview=lecture.raw_text[:400]
    )


@app.post("/api/process/{lecture_id}", response_model=schemas.ProcessOut)
def process_lecture(lecture_id: int, db: Session = Depends(get_db)):
    lecture = crud.get_lecture(db, lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    summary = summarize_text(lecture.raw_text, max_sentences=4)
    keywords = extract_keywords(lecture.raw_text, top_n=10)
    questions = generate_quiz_questions(keywords)

    crud.create_or_update_result(db, lecture_id, summary, keywords, questions)

    return schemas.ProcessOut(
        lecture_id=lecture_id,
        summary=summary,
        keywords=keywords,
        questions=questions,
    )


@app.get("/api/lectures/{lecture_id}", response_model=schemas.LectureDetailOut)
def get_lecture_detail(lecture_id: int, db: Session = Depends(get_db)):
    lecture = crud.get_lecture(db, lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    result = lecture.result
    keywords: List[str] = result.keywords.split(",") if result and result.keywords else []
    questions: List[str] = result.questions.split("\n") if result and result.questions else []

    return schemas.LectureDetailOut(
        id=lecture.id,
        filename=lecture.filename,
        summary=result.summary if result else None,
        keywords=keywords,
        questions=questions,
    )

origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
if not origins:
    origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)