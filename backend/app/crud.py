from sqlalchemy.orm import Session
from . import models


def create_lecture(db: Session, filename: str, filepath: str, raw_text: str):
    lecture = models.Lecture(filename=filename, filepath=filepath, raw_text=raw_text)
    db.add(lecture)
    db.commit()
    db.refresh(lecture)
    return lecture


def get_lecture(db: Session, lecture_id: int):
    return db.query(models.Lecture).filter(models.Lecture.id == lecture_id).first()


def create_or_update_result(db: Session, lecture_id: int, summary: str, keywords: list[str], questions: list[str]):
    existing = db.query(models.Result).filter(models.Result.lecture_id == lecture_id).first()
    kw_text = ",".join(keywords)
    q_text = "\n".join(questions)

    if existing:
        existing.summary = summary
        existing.keywords = kw_text
        existing.questions = q_text
        db.commit()
        db.refresh(existing)
        return existing

    result = models.Result(
        lecture_id=lecture_id,
        summary=summary,
        keywords=kw_text,
        questions=q_text,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result