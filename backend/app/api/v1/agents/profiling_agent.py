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
                # Try ML model first
                ml_result = await self._get_ml_profile(offender_data)

                if ml_result and ml_result.get("status") == "success":
                    # Use XGBoost + SHAP result
                    result = {
                        "archetype": ml_result.get("archetype", "Unknown"),
                        "risk_level": self._score_to_level(ml_result.get("risk_score", 0.5)),
                        "risk_score": ml_result.get("risk_score", 0.5),
                        "recidivism_probability": ml_result.get("recidivism_probability", 0.5),
                        "escalation_risk": ml_result.get("escalation_risk", "Medium"),
                        "behavioral_patterns": self._extract_patterns(ml_result),
                        "profile_summary": f"ML-assessed profile: {ml_result.get('archetype', 'Unknown')} archetype with risk score {ml_result.get('risk_score', 0):.2f}",
                        "shap_explanation": ml_result.get("shap_explanation", {}),
                        "model_used": "XGBoost + SHAP",
                    }
                    state["profiling_result"] = result
                    state["reasoning_chain"].append(
                        f"Profiling Agent (ML): {result['archetype']} - Risk: {result['risk_level']} ({result['risk_score']:.2f})"
                    )
                else:
                    # Fallback to LLM-based profiling
                    response = await client.chat.completions.create(
                        model=settings.OPENAI_MODEL,
                        messages=[
                            {"role": "system", "content": PROFILING_PROMPT.format(
                                data=json.dumps(offender_data, indent=2, default=str)
                            )},
                        ],
                        temperature=0.2,
                        max_tokens=500,
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
                            "archetype": "Unknown",
                            "risk_level": "Medium",
                            "risk_score": 0.5,
                            "recidivism_probability": 0.5,
                            "escalation_risk": "Medium",
                            "behavioral_patterns": ["Unknown patterns"],
                            "profile_summary": f"Could not parse profiling response: {str(e)}"
                        }
                    result["model_used"] = "LLM"
                    state["profiling_result"] = result
                    state["reasoning_chain"].append(
                        f"Profiling Agent (LLM): {result.get('archetype')} - Risk: {result.get('risk_level')} ({result.get('risk_score')})"
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

    async def _get_ml_profile(self, offender_data: dict) -> dict:
        """Try to get prediction from trained XGBoost model."""
        try:
            from app.ml.profiling import predict_risk

            # Map DB offender data to model features
            features = {
                "age": offender_data.get("age") or 30,
                "prior_cases": offender_data.get("prior_cases") or 0,
                "is_repeat_offender": 1 if offender_data.get("is_repeat_offender") else 0,
                "education_score": self._education_to_score(offender_data.get("education_level")),
                "employment_score": 1 if offender_data.get("occupation") else 0,
                "is_male": 1 if str(offender_data.get("gender", "")).lower() in ("male", "m") else 0,
                "substance_abuse": 0,
                "gang_affiliation": 0,
                "mental_health_issues": 0,
                "weapon_use": 0,
                "violence_score": min((offender_data.get("prior_cases") or 0) * 0.2, 1.0),
            }

            return await predict_risk(features)
        except Exception:
            return {}

    def _education_to_score(self, edu: str) -> int:
        if not edu:
            return 2
        edu_map = {"illiterate": 0, "primary": 1, "secondary": 2, "higher_secondary": 3, "graduate": 4, "post_graduate": 5}
        return edu_map.get(edu.lower().replace(" ", "_"), 2)

    def _score_to_level(self, score: float) -> str:
        if score >= 0.8:
            return "Critical"
        if score >= 0.6:
            return "High"
        if score >= 0.4:
            return "Medium"
        return "Low"

    def _extract_patterns(self, ml_result: dict) -> list:
        patterns = []
        shap = ml_result.get("shap_explanation", {})
        # Top positive SHAP features indicate behavioral patterns
        sorted_features = sorted(shap.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        for feat, val in sorted_features:
            if val > 0:
                patterns.append(f"High {feat.replace('_', ' ')}")
            else:
                patterns.append(f"Low {feat.replace('_', ' ')}")
        return patterns or ["Data-driven assessment"]

    async def _extract_person_id(self, query: str) -> str:
        prompt = f"""Extract the person name, phone number, aadhaar number, case ID, or person ID from the following query. 
If none is specified, return "unknown".
Return ONLY the extracted identifier, nothing else.

Query: {query}"""
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.0,
                max_tokens=50,
            )
            extracted = response.choices[0].message.content.strip()
            extracted = extracted.replace('"', '').replace("'", '').strip()
            return extracted
        except Exception:
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
                LEFT JOIN firs f ON ci.fir_id = f.id
                WHERE CAST(p.id AS VARCHAR) = :pid 
                   OR p.phone = :pid 
                   OR p.aadhaar_number = :pid
                   OR p.first_name ILIKE :name
                   OR p.last_name ILIKE :name
                   OR (p.first_name || ' ' || p.last_name) ILIKE :name
                   OR f.fir_number ILIKE :name
                GROUP BY p.id, p.first_name, p.last_name, p.gender, p.date_of_birth,
                         p.occupation, p.education_level
            """)
            result = await session.execute(sql.bindparams(pid=person_id, name=f"%{person_id}%"))
            row = result.fetchone()
            return dict(row._mapping) if row else {}
