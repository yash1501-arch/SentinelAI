import base64
import tempfile
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


class VoiceTranscribeResponse(BaseModel):
    status: str
    transcript: str
    language: str
    confidence: float
    translation_en: Optional[str] = None
    duration_seconds: float


@router.post("/transcribe", response_model=VoiceTranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("en"),
    current_user: User = Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio type")

    audio_bytes = await file.read()

    suffix = ".webm"
    if file.filename:
        _, ext = os.path.splitext(file.filename)
        if ext:
            suffix = ext

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language if language in ("kn", "hi", "ta", "te", "mr") else None,
                response_format="verbose_json",
            )

        result = VoiceTranscribeResponse(
            status="success",
            transcript=transcript.text,
            language=language,
            confidence=round(
                transcript.segments[0].get("confidence", 0.95)
                if getattr(transcript, "segments", None)
                else 0.95,
                4,
            ),
            duration_seconds=round(getattr(transcript, "duration", 0), 2),
        )

        if language == "kn":
            with open(tmp_path, "rb") as audio_file:
                translation = client.audio.translations.create(
                    model="whisper-1",
                    file=audio_file,
                )
            result.translation_en = translation.text

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        os.unlink(tmp_path)


@router.post("/transcribe-base64")
async def transcribe_base64(
    audio_base64: str,
    language: str = "en",
    current_user: User = Depends(get_current_user),
):
    try:
        audio_bytes = base64.b64decode(audio_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 audio data")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language if language in ("kn", "hi", "ta", "te", "mr") else None,
                response_format="verbose_json",
            )

        return {
            "status": "success",
            "transcript": transcript.text,
            "language": language,
            "confidence": round(
                transcript.segments[0].get("confidence", 0.95)
                if getattr(transcript, "segments", None)
                else 0.95,
                4,
            ),
            "duration_seconds": round(getattr(transcript, "duration", 0), 2),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        os.unlink(tmp_path)
