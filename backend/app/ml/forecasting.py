"""
Crime forecasting ML integration using Prophet.

Wraps the ml-services/forecasting module for use within the FastAPI backend.
"""
import os
import sys
import json
import asyncio
from typing import Optional
from pathlib import Path
from loguru import logger

# Add ml-services to path for imports
ML_SERVICES_DIR = Path(__file__).resolve().parents[2] / "ml-services"
sys.path.insert(0, str(ML_SERVICES_DIR))

MODELS_DIR = ML_SERVICES_DIR / "forecasting" / "models"


async def run_forecast(days: int = 30, crime_type: Optional[str] = None) -> dict:
    """Generate crime forecast for the given number of days."""
    try:
        model_path = MODELS_DIR / "prophet_model.pkl"
        if not model_path.exists():
            logger.info("Prophet model not found, training...")
            await train_model()

        predictions = await asyncio.to_thread(_predict_sync, days)
        return {
            "status": "success",
            "forecast_days": days,
            "crime_type": crime_type or "all",
            "predictions": predictions,
            "model_metrics": _load_metrics(),
        }
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "predictions": [],
        }


async def train_model() -> dict:
    """Train the Prophet forecasting model."""
    try:
        from forecasting.model import train
        result = await asyncio.to_thread(train)
        logger.info(f"Prophet model trained: {result}")
        return result
    except Exception as e:
        logger.error(f"Model training error: {e}")
        return {"status": "error", "error": str(e)}


def _predict_sync(days: int) -> list:
    """Synchronous prediction wrapper."""
    try:
        from forecasting.model import predict
        return predict(days)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return []


def _load_metrics() -> dict:
    """Load stored model metrics."""
    metrics_path = MODELS_DIR / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            return json.load(f)
    return {}
