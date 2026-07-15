import json
import time
from sqlalchemy import text
from app.core.config import settings
from app.services.openai_client import create_openai_client
from app.core.database import async_session_factory
from app.llm.state import AgentState

client = create_openai_client()

SQL_PROMPT = """
You are the SQL Agent for Sentinel AI. Convert natural language into PostgreSQL SQL queries.

Database Schema:
- firs(id, fir_number, police_station, district, state, registration_date, act_sections, brief_fact, recorded_by, io_name)
- crime_incidents(id, fir_id, crime_type_id, incident_date, incident_time, description, modus_operandi, property_value_loss, injury_count, fatality_count, is_solved, is_heinous, day_of_week, time_period)
- crime_types(id, name, category, severity_level, is_bailable, is_cognizable)
- persons(id, first_name, middle_name, last_name, alias, date_of_birth, gender, nationality, occupation, phone, aadhaar_number)
- victims(id, person_id, incident_id, injury_description, property_loss, is_minor)
- accused(id, person_id, incident_id, arrest_date, charge_sections, bail_status, is_repeat_offender, risk_score)
- witnesses(id, person_id, incident_id, witness_type, is_eye_witness, credibility_score)
- bank_accounts(id, account_number, ifsc_code, bank_name, person_id)
- transactions(id, from_account_id, to_account_id, amount, transaction_date, is_suspicious)
- gangs(id, name, territory, primary_crime_type, risk_level)

Rules:
- Return ONLY valid PostgreSQL SQL
- Use parameterized naming conventions
- Add LIMIT 100 unless specified otherwise
- Use appropriate JOINs through foreign keys
- For time ranges use: incident_date >= CURRENT_DATE - INTERVAL 'N months'
- For text search use: ILIKE for case-insensitive matching
- For date filtering use: BETWEEN or >= / <= operators

User Query: {query}
Previous Context: {context}

Respond ONLY with a JSON object:
{{"sql": "SELECT ...", "explanation": "brief explanation", "tables_used": ["table1", "table2"]}}
"""


class SQLAgent:
    async def run(self, state: AgentState) -> AgentState:
        start = time.time()
        context = self._format_context(state.get("context", []))

        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SQL_PROMPT.format(query=state["query"], context=context)},
                ],
                temperature=0.0,
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
                    "sql": "",
                    "explanation": f"Could not parse SQL agent response: {str(e)}",
                    "tables_used": []
                }
            sql_query = result.get("sql", "").strip()
            state["sql_query"] = sql_query
            state["reasoning_chain"].append(f"SQL Agent generated: {result.get('explanation', '')}")

            if sql_query:
                state["sql_result"] = await self._execute_sql(sql_query)
                state["reasoning_chain"].append(
                    f"SQL Agent executed query, returned {len(state['sql_result'])} rows"
                )
            else:
                state["sql_result"] = []
                state["sql_error"] = "Empty SQL generated"

        except Exception as e:
            state["sql_error"] = str(e)
            state["sql_result"] = []
            state["reasoning_chain"].append(f"SQL Agent error: {str(e)}")

        state["processing_time_ms"] = int((time.time() - start) * 1000)
        return state

    async def _execute_sql(self, sql: str) -> list:
        async with async_session_factory() as session:
            try:
                result = await session.execute(text(sql))
                columns = result.keys()
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            except Exception as e:
                raise e

    def _format_context(self, context: list) -> str:
        if not context:
            return "No previous context"
        return "\n".join([f"{c['role']}: {c['content'][:200]}" for c in context[-3:]])
