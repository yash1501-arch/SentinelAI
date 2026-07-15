import sys
import asyncio
from pathlib import Path

ML_SERVICES_DIR = Path(__file__).resolve().parents[2] / "ml-services"
sys.path.insert(0, str(ML_SERVICES_DIR))


async def analyze_sociological() -> dict:
    try:
        from sociological.model import analyze
        result = await asyncio.to_thread(analyze, False)
        return result if isinstance(result, dict) else {}
    except Exception:
        return {}
