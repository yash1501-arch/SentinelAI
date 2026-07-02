"""
Offender profiling ML integration using XGBoost + SHAP.

Wraps the ml-services/profiling module for use within the FastAPI backend.
"""
import os
import sys
import json
import asyncio
from typing import Optional
from pathlib import Path
from loguru import logger

ML_SERVICES_DIR = Path(__file__).resolve().parents[2] / "ml-services"
sys.path.insert(0, str(ML_SERVICES_DIR))

MODELS_DIR = ML_SERVICES_DIR / "profiling" / "models"


async def predict_risk(features: dict) -> dict:
    """Predict offender risk score with SHAP explanations."""
    try:
        model_path = MODELS_DIR / "risk_model.pkl"
        if not model_path.exists():
            logger.info("Profiling models not found, training...")
            await train_model()

        result = await asyncio.to_thread(_predict_sync, features)
        return {
            "status": "success",
            **result,
        }
    except Exception as e:
        logger.error(f"Profiling prediction error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "risk_score": 0.0,
        }


async def train_model() -> dict:
    """Train the XGBoost profiling models."""
    try:
        from profiling.model import train
        result = await asyncio.to_thread(train)
        logger.info(f"Profiling models trained: {result}")
        return result
    except Exception as e:
        logger.error(f"Profiling training error: {e}")
        return {"status": "error", "error": str(e)}


def _predict_sync(features: dict) -> dict:
    """Synchronous prediction wrapper."""
    from profiling.model import predict
    return predict(features)


def _load_metrics() -> dict:
    """Load stored model metrics."""
    metrics_path = MODELS_DIR / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            return json.load(f)
    return {}
