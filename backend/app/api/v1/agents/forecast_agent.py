import time
import json
from sqlalchemy import text
from app.core.config import settings
from app.services.openai_client import create_openai_client
from app.core.database import async_session_factory
from app.llm.state import AgentState

client = create_openai_client()

FORECAST_PROMPT = """
You are the Forecast Agent for Sentinel AI. Analyze crime data patterns and provide predictive insights.

Historical Data Summary: {data}
ML Model Forecast: {ml_forecast}
User Query: {query}

Provide a structured forecast analysis with:
1. Predicted trends (increasing/decreasing/stable)
2. Expected hotspots
3. Seasonal patterns
4. Confidence assessment

Respond with JSON:
{{
    "trend_direction": "increasing|decreasing|stable",
    "trend_magnitude": "slight|moderate|significant",
    "predicted_hotspots": ["area1", "area2"],
    "seasonal_patterns": ["pattern1"],
    "confidence_level": 0.0-1.0,
    "key_insights": ["insight1", "insight2"],
    "alert_recommendation": "none|low|medium|high",
    "forecast_data": []
}}
"""


class ForecastAgent:
    async def run(self, state: AgentState) -> AgentState:
        start = time.time()

        try:
            historical_data = await self._get_historical_data(state["query"])

            # Try to get Prophet model predictions
            ml_forecast = await self._get_ml_forecast()

            # Gang activity forecast
            gang_forecast = await self._get_gang_forecast(state["query"])
            historical_data["gang_forecast"] = gang_forecast

            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": FORECAST_PROMPT.format(
                        data=json.dumps(historical_data, indent=2, default=str),
                        ml_forecast=json.dumps(ml_forecast, indent=2, default=str),
                        query=state["query"],
                    )},
                ],
                temperature=0.2,
                max_tokens=600,
            )

            raw = response.choices[0].message.content.strip()
            try:
                import re
                match = re.search(r"(\{.*\})", raw, re.DOTALL)
                raw_json = match.group(1) if match else raw
                cleaned = []
                in_string = False
                escape = False
                for char in raw_json:
                    if char == '"' and not escape:
                        in_string = not in_string
                        cleaned.append(char)
                    elif char == '\\' and in_string and not escape:
                        escape = True
                        cleaned.append(char)
                    else:
                        if char == '\n' and in_string:
                            cleaned.append('\\n')
                        elif char == '\r' and in_string:
                            cleaned.append('\\r')
                        else:
                            cleaned.append(char)
                        escape = False
                result = json.loads("".join(cleaned))
            except Exception as e:
                import traceback
                traceback.print_exc()
                result = {
                    "trend_direction": "stable",
                    "trend_magnitude": "slight",
                    "predicted_hotspots": [],
                    "seasonal_patterns": [],
                    "confidence_level": 0.5,
                    "key_insights": [f"Could not parse model output: {str(e)}"],
                    "alert_recommendation": "none",
                    "forecast_data": []
                }

            # Merge ML forecast data into result if available
            if ml_forecast and ml_forecast.get("predictions"):
                result["forecast_data"] = ml_forecast["predictions"][:30]
                result["model_used"] = "Prophet"
                result["model_metrics"] = ml_forecast.get("model_metrics", {})

            state["forecast_result"] = result
            state["reasoning_chain"].append(
                f"Forecast Agent: trend={result.get('trend_direction')}, confidence={result.get('confidence_level')}, model={'Prophet' if ml_forecast.get('predictions') else 'LLM-only'}"
            )

        except Exception as e:
            state["forecast_error"] = str(e)
            state["forecast_result"] = {}
            state["reasoning_chain"].append(f"Forecast Agent error: {str(e)}")

        state["processing_time_ms"] = int((time.time() - start) * 1000)
        return state

    async def _get_ml_forecast(self) -> dict:
        """Try to get predictions from the trained Prophet model."""
        try:
            from app.ml.forecasting import run_forecast
            result = await run_forecast(days=30)
            if result.get("status") == "success":
                return result
        except Exception:
            pass
        return {}

    async def _get_gang_forecast(self, query: str) -> dict:
        try:
            async with async_session_factory() as session:
                sql = text("""
                    SELECT
                        g.name as gang_name,
                        COUNT(DISTINCT ci.id) as incident_count,
                        COUNT(DISTINCT a.person_id) as member_count,
                        MIN(ci.incident_date) as first_seen,
                        MAX(ci.incident_date) as last_seen,
                        STRING_AGG(DISTINCT ct.name, ', ') as crime_types
                    FROM gangs g
                    JOIN gang_members gm ON g.id = gm.gang_id
                    JOIN accused a ON gm.person_id = a.person_id
                    JOIN crime_incidents ci ON a.incident_id = ci.id
                    JOIN crime_types ct ON ci.crime_type_id = ct.id
                    WHERE ci.incident_date >= CURRENT_DATE - INTERVAL '12 months'
                    GROUP BY g.id, g.name
                    ORDER BY incident_count DESC
                    LIMIT 10
                """)
                result = await session.execute(sql)
                rows = [dict(r._mapping) for r in result]

                for row in rows:
                    if row.get("last_seen") and row.get("first_seen"):
                        delta = (row["last_seen"] - row["first_seen"]).days
                        row["active_days"] = delta
                        row["escalation_score"] = round(
                            min(1.0, (row["incident_count"] / max(row["member_count"], 1)) * 0.3 + 0.1), 4
                        )
                return {"gangs": rows, "total_gangs": len(rows)}
        except Exception:
            return {"gangs": [], "total_gangs": 0}

    async def _get_historical_data(self, query: str) -> dict:
        async with async_session_factory() as session:
            monthly = text("""
                SELECT
                    date_trunc('month', incident_date) as month,
                    COUNT(*) as total_cases
                FROM crime_incidents
                WHERE incident_date >= CURRENT_DATE - INTERVAL '24 months'
                GROUP BY month ORDER BY month
            """)
            type_dist = text("""
                SELECT ct.name, COUNT(*) as count
                FROM crime_incidents ci
                JOIN crime_types ct ON ci.crime_type_id = ct.id
                WHERE ci.incident_date >= CURRENT_DATE - INTERVAL '12 months'
                GROUP BY ct.name ORDER BY count DESC
            """)
            by_day = text("""
                SELECT day_of_week, COUNT(*) as count
                FROM crime_incidents
                WHERE day_of_week IS NOT NULL
                GROUP BY day_of_week ORDER BY count DESC
            """)

            monthly_data = [dict(r._mapping) for r in await session.execute(monthly)]
            type_data = [dict(r._mapping) for r in await session.execute(type_dist)]
            day_data = [dict(r._mapping) for r in await session.execute(by_day)]

            return {
                "monthly_trend": monthly_data,
                "crime_type_distribution": type_data,
                "day_of_week_pattern": day_data,
                "total_months_analyzed": len(monthly_data),
            }
