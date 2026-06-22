import time
from datetime import datetime, timezone, timedelta
from sqlalchemy import text
from app.core.database import async_session_factory
from app.llm.state import AgentState


class AnalyticsAgent:
    async def run(self, state: AgentState) -> AgentState:
        start = time.time()

        try:
            query = state["query"].lower()
            results = {}

            if any(w in query for w in ["trend", "trending", "increase", "decrease", "over time", "monthly", "weekly"]):
                results["trends"] = await self._get_crime_trends(query)

            if any(w in query for w in ["hotspot", "cluster", "area", "zone", "map"]):
                results["hotspots"] = await self._get_hotspots(query)

            if any(w in query for w in ["statistic", "count", "total", "how many", "summary"]):
                results["statistics"] = await self._get_statistics(query)

            if any(w in query for w in ["demographic", "sociological", "age", "gender", "income", "education", "correlation"]):
                results["sociological"] = await self._get_sociological_insights(query)

            if any(w in query for w in ["season", "month", "day of week", "time", "pattern"]):
                results["patterns"] = await self._get_temporal_patterns(query)

            state["analytics_result"] = results if results else {"message": "No specific analytics matched"}
            state["reasoning_chain"].append(
                f"Analytics Agent completed: {list(results.keys())}"
            )

        except Exception as e:
            state["analytics_error"] = str(e)
            state["analytics_result"] = {}
            state["reasoning_chain"].append(f"Analytics Agent error: {str(e)}")

        state["processing_time_ms"] = int((time.time() - start) * 1000)
        return state

    async def _get_crime_trends(self, query: str) -> list:
        months = 12
        async with async_session_factory() as session:
            sql = text("""
                SELECT
                    date_trunc('month', incident_date) as month,
                    ct.name as crime_type,
                    COUNT(*) as count
                FROM crime_incidents ci
                JOIN crime_types ct ON ci.crime_type_id = ct.id
                WHERE ci.incident_date >= CURRENT_DATE - INTERVAL ':months months'
                GROUP BY month, ct.name
                ORDER BY month DESC, count DESC
                LIMIT 50
            """)
            result = await session.execute(sql.bindparams(months=str(months)))
            return [dict(row._mapping) for row in result]

    async def _get_hotspots(self, query: str) -> list:
        async with async_session_factory() as session:
            sql = text("""
                SELECT latitude, longitude, COUNT(*) as crime_count,
                       STRING_AGG(DISTINCT ct.name, ', ') as crime_types
                FROM locations l
                JOIN crime_incidents ci ON l.incident_id = ci.id
                JOIN crime_types ct ON ci.crime_type_id = ct.id
                WHERE ci.incident_date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY latitude, longitude
                HAVING COUNT(*) > 2
                ORDER BY crime_count DESC
                LIMIT 20
            """)
            result = await session.execute(sql)
            return [dict(row._mapping) for row in result]

    async def _get_statistics(self, query: str) -> dict:
        async with async_session_factory() as session:
            sql = text("""
                SELECT
                    COUNT(*) as total_cases,
                    COUNT(*) FILTER (WHERE is_solved) as solved_cases,
                    COUNT(*) FILTER (WHERE is_heinous) as heinous_cases,
                    SUM(injury_count) as total_injuries,
                    SUM(fatality_count) as total_fatalities,
                    ROUND(AVG(property_value_loss)::numeric, 2) as avg_loss
                FROM crime_incidents
                WHERE incident_date >= CURRENT_DATE - INTERVAL '12 months'
            """)
            result = await session.execute(sql)
            row = result.fetchone()
            return dict(row._mapping) if row else {}

    async def _get_sociological_insights(self, query: str) -> list:
        async with async_session_factory() as session:
            sql = text("""
                SELECT
                    p.gender, p.occupation, p.education_level,
                    ct.category as crime_category,
                    COUNT(*) as count
                FROM persons p
                JOIN accused a ON p.id = a.person_id
                JOIN crime_incidents ci ON a.incident_id = ci.id
                JOIN crime_types ct ON ci.crime_type_id = ct.id
                WHERE p.gender IS NOT NULL
                GROUP BY p.gender, p.occupation, p.education_level, ct.category
                ORDER BY count DESC
                LIMIT 20
            """)
            result = await session.execute(sql)
            return [dict(row._mapping) for row in result]

    async def _get_temporal_patterns(self, query: str) -> dict:
        async with async_session_factory() as session:
            day_sql = text("""
                SELECT day_of_week, COUNT(*) as count
                FROM crime_incidents
                WHERE day_of_week IS NOT NULL
                GROUP BY day_of_week ORDER BY count DESC
            """)
            time_sql = text("""
                SELECT time_period, COUNT(*) as count
                FROM crime_incidents
                WHERE time_period IS NOT NULL
                GROUP BY time_period ORDER BY count DESC
            """)
            days = await session.execute(day_sql)
            times = await session.execute(time_sql)
            return {
                "by_day": [dict(row._mapping) for row in days],
                "by_time": [dict(row._mapping) for row in times],
            }
