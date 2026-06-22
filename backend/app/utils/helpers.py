import uuid
import hashlib
from datetime import datetime, timezone
from typing import Optional


def generate_uuid() -> str:
    return str(uuid.uuid4())


def hash_id(*parts: str) -> str:
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%d/%m/%Y",
        "%d-%m-%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def calculate_age(dob: datetime, reference_date: Optional[datetime] = None) -> int:
    if not reference_date:
        reference_date = datetime.now(timezone.utc)
    return reference_date.year - dob.year - (
        (reference_date.month, reference_date.day) < (dob.month, dob.day)
    )


def mask_pii(value: str, visible_chars: int = 4) -> str:
    if len(value) <= visible_chars:
        return value
    return value[:visible_chars] + "*" * (len(value) - visible_chars)


def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


class CaseInsensitiveDict(dict):
    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def __contains__(self, key):
        return super().__contains__(key.lower())
