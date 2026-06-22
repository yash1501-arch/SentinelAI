import json
import base64
import os
import tempfile
from openai import OpenAI


def handler(event, context):
    try:
        body = event.get("body", {})
        audio_b64 = body.get("audio", "")
        language = body.get("language", "en")
        session_id = body.get("session_id", "")

        if not audio_b64:
            return {"status": "error", "message": "No audio data provided"}

        audio_bytes = base64.b64decode(audio_b64)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

            with open(tmp_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language if language in ("kn", "hi", "ta", "te", "mr") else None,
                    response_format="verbose_json",
                )

            result = {
                "status": "success",
                "transcript": transcript.text,
                "language": language,
                "confidence": round(
                    transcript.segments[0].get("confidence", 0.95)
                    if getattr(transcript, "segments", None)
                    else 0.95,
                    4,
                ),
                "session_id": session_id,
                "duration_seconds": round(getattr(transcript, "duration", 0), 2),
            }

            if language == "kn":
                with open(tmp_path, "rb") as audio_file:
                    translation = client.audio.translations.create(
                        model="whisper-1",
                        file=audio_file,
                    )
                result["translation_en"] = translation.text

        finally:
            os.unlink(tmp_path)

        return result

    except Exception as e:
        return {"status": "error", "message": str(e)}
