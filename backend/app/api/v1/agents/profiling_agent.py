import time
import json
from sqlalchemy import text
from app.core.config import settings
from app.services.openai_client import create_openai_client
from app.core.database import async_session_factory
from app.llm.state import AgentState

client = create_openai_client()

PROFILING_PROMPT = """
You are the Profiling Agent for Sentinel AI. Analyze offender data and generate behavioral profiles.

Based on the available data, classify the offender into one of these archetypes:
1. Opportunistic Offender - Impulsive, situational, low planning
2. Organized Criminal - Pre-planned, structured, methodical
3. Violent Predator - Aggressive pattern, escalation risk
4. Financial Fraudster - White-collar, deception-based
5. Gang Associate - Group-affiliated, territory-driven
6. Situational Offender - Circumstance-driven, one-time

Offender Data: {data}

Respond with JSON:
{{
    "archetype": "archetype name",
    "risk_level": "Low|Medium|High|Critical",
    "risk_score": 0.0-1.0,
    "recidivism_probability": 0.0-1.0,
    "escalation_risk": "Low|Medium|High",
    "behavioral_patterns": ["pattern1", "pattern2"],
    "profile_summary": "2-3 sentence summary"
}}
"""


class ProfilingAgent:
    async def run(self, state: AgentState) -> AgentState:
        start = time.time()

        try:
            person_id = await self._extract_person_id(state["query"])
            offender_data = await self._get_offender_data(person_id)

            if offender_data:
                response = await client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": PROFILING_PROMPT.format(
                            data=json.dumps(offender_data, indent=2)
                        )},
                    ],
                    temperature=0.2,
                    max_tokens=500,
                )
                result = json.loads(response.choices[0].message.content.strip())
                state["profiling_result"] = result
                state["reasoning_chain"].append(
                    f"Profiling Agent: {result.get('archetype')} - Risk: {result.get('risk_level')} ({result.get('risk_score')})"
                )
            else:
                state["profiling_result"] = {"message": "Insufficient data for profiling"}
                state["reasoning_chain"].append("Profiling Agent: insufficient data")

        except Exception as e:
            state["profiling_error"] = str(e)
            state["profiling_result"] = {}
            state["reasoning_chain"].append(f"Profiling Agent error: {str(e)}")

        state["processing_time_ms"] = int((time.time() - start) * 1000)
        return state

    async def _extract_person_id(self, query: str) -> str:
        return query

    async def _get_offender_data(self, person_id: str) -> dict:
        async with async_session_factory() as session:
            sql = text("""
                SELECT
                    p.id, p.first_name, p.last_name, p.gender,
                    EXTRACT(YEAR FROM AGE(p.date_of_birth))::int as age,
                    p.occupation, p.education_level,
                    COUNT(DISTINCT a.id) as prior_cases,
                    BOOL_OR(a.is_repeat_offender) as is_repeat_offender,
                    AVG(a.risk_score) as avg_risk_score,
                    STRING_AGG(DISTINCT ct.name, ', ') as crime_types
                FROM persons p
                LEFT JOIN accused a ON p.id = a.person_id
                LEFT JOIN crime_incidents ci ON a.incident_id = ci.id
                LEFT JOIN crime_types ct ON ci.crime_type_id = ct.id
                WHERE p.id = :pid OR p.phone = :pid OR p.aadhaar_number = :pid
                GROUP BY p.id, p.first_name, p.last_name, p.gender, p.date_of_birth,
                         p.occupation, p.education_level
            """)
            result = await session.execute(sql.bindparams(pid=person_id))
            row = result.fetchone()
            return dict(row._mapping) if row else {}
