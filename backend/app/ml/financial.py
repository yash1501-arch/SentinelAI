"""
Financial fraud detection using Isolation Forest + XGBoost.

Wraps the ml-services/financial module for use within the FastAPI backend.
"""
import sys
import json
import asyncio
from pathlib import Path
from loguru import logger

ML_SERVICES_DIR = Path(__file__).resolve().parents[2] / "ml-services"
sys.path.insert(0, str(ML_SERVICES_DIR))

MODELS_DIR = ML_SERVICES_DIR / "financial" / "models"


async def detect_fraud(transaction: dict) -> dict:
    """Predict whether a transaction is fraudulent."""
    try:
        model_path = MODELS_DIR / "xgb_fraud_model.pkl"
        if not model_path.exists():
            logger.info("Financial models not found, training...")
            await train_model()

        result = await asyncio.to_thread(_predict_sync, transaction)
        return {
            "status": "success",
            **result,
        }
    except Exception as e:
        logger.error(f"Fraud detection error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "is_fraudulent": False,
        }


async def train_model() -> dict:
    """Train the financial fraud detection models."""
    try:
        from financial.model import train
        result = await asyncio.to_thread(train)
        logger.info(f"Financial models trained: {result}")
        return result
    except Exception as e:
        logger.error(f"Financial training error: {e}")
        return {"status": "error", "error": str(e)}


def _predict_sync(transaction: dict) -> dict:
    """Synchronous prediction wrapper."""
    from financial.model import predict
    return predict(transaction)
