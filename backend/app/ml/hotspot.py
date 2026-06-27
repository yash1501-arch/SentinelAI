"""
Crime hotspot detection using DBSCAN clustering.

Wraps the ml-services/hotspot module for use within the FastAPI backend.
"""
import sys
import json
import asyncio
from pathlib import Path
from loguru import logger

ML_SERVICES_DIR = Path(__file__).resolve().parents[3] / "ml-services"
sys.path.insert(0, str(ML_SERVICES_DIR))

MODELS_DIR = ML_SERVICES_DIR / "hotspot" / "models"


async def detect_hotspots(eps: float = 0.01, min_samples: int = 5) -> dict:
    """Run DBSCAN clustering to detect crime hotspots."""
    try:
        result = await asyncio.to_thread(_detect_sync, eps, min_samples)
        return {
            "status": "success",
            "hotspots": result,
            "count": len(result),
            "params": {"eps": eps, "min_samples": min_samples},
        }
    except Exception as e:
        logger.error(f"Hotspot detection error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "hotspots": [],
        }


def _detect_sync(eps: float, min_samples: int) -> list:
    """Synchronous hotspot detection."""
    try:
        from hotspot.model import detect_hotspots as _detect
        return _detect(eps=eps, min_samples=min_samples)
    except Exception as e:
        logger.error(f"Hotspot sync error: {e}")
        return []
