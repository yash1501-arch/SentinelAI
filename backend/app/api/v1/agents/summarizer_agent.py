import time
import json
from app.core.config import settings
from app.services.openai_client import create_openai_client
from app.llm.state import AgentState

client = create_openai_client()

SUMMARIZER_PROMPT = """
You are the Summarizer Agent for Sentinel AI. Generate clear, evidence-backed responses for law enforcement personnel.

Guidelines:
- Start with a direct, concise answer
- Include specific numbers and facts
- Cite sources with confidence scores
- If confidence < 0.7, explicitly state uncertainty
- Format for readability (bullet points, sections)
- Suggest relevant follow-up questions
- NEVER invent information not present in the agent results

User Query: {query}
Intent: {intent}
Confidence: {confidence}

Agent Results:
--- SQL Agent ---
{sql_result}

--- Graph Agent ---
{graph_result}

--- RAG Agent ---
{rag_result}

--- Analytics Agent ---
{analytics_result}

--- Profiling Agent ---
{profiling_result}

--- Forecast Agent ---
{forecast_result}

Reasoning Chain:
{reasoning_chain}

Generate response in {language}.
Keep responses concise. Use markdown formatting for readability.

Respond ONLY with a JSON object:
{{
    "response": "complete response text",
    "sources": [{{"type": "source", "detail": "description"}}],
    "confidence_score": 0.0-1.0,
    "suggested_questions": ["q1", "q2"]
}}
"""


class SummarizerAgent:
    async def run(self, state: AgentState) -> AgentState:
        start = time.time()

        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SUMMARIZER_PROMPT.format(
                        query=state["query"],
                        intent=state.get("intent", "general").value if state.get("intent") else "general",
                        confidence=state.get("intent_confidence", 0.5),
                        sql_result=self._format_result(state.get("sql_result", [])),
                        graph_result=self._format_result(state.get("graph_result", [])),
                        rag_result=self._format_result(state.get("rag_result", [])),
                        analytics_result=json.dumps(state.get("analytics_result", {}), indent=2, default=str)[:2000],
                        profiling_result=json.dumps(state.get("profiling_result", {}), indent=2, default=str)[:2000],
                        forecast_result=json.dumps(state.get("forecast_result", {}), indent=2, default=str)[:2000],
                        reasoning_chain="\n".join(state.get("reasoning_chain", [])),
                        language=state.get("language", "English"),
                    )},
                ],
                temperature=0.3,
                max_tokens=1000,
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
                    "response": raw if 'raw' in locals() else f"I could not summarize the results correctly: {str(e)}",
                    "sources": [],
                    "confidence_score": 0.5,
                    "suggested_questions": []
                }
            state["response"] = result.get("response", "")
            state["sources"] = result.get("sources", [])
            state["confidence_score"] = float(result.get("confidence_score", 0.5))
            state["reasoning_chain"].append("Summarizer generated final response")

            follow_ups = result.get("suggested_questions", [])
            if follow_ups:
                state["response"] += "\n\n**Suggested follow-ups:**\n" + "\n".join(
                    [f"- {q}" for q in follow_ups]
                )

        except Exception as e:
            import traceback
            traceback.print_exc()
            state["reasoning_chain"].append(f"Summarizer fallback: {str(e)}")
            state["response"] = f"Based on the analysis of your query: **{state['query']}**\n\n"
            if state.get("sql_result"):
                state["response"] += f"- SQL result: {len(state['sql_result'])} records found.\n"
            if state.get("graph_result"):
                state["response"] += f"- Graph result: {len(state['graph_result'])} records found.\n"
            if state.get("rag_result"):
                state["response"] += f"- RAG search: {len(state['rag_result'])} relevant documents found.\n"
            if state.get("analytics_result"):
                state["response"] += "- Pattern analysis completed.\n"
            if state.get("profiling_result") and "archetype" in state["profiling_result"]:
                state["response"] += f"- Offender profile: {state['profiling_result'].get('archetype')} - Risk: {state['profiling_result'].get('risk_level')}\n"
            if state.get("forecast_result") and "trend_direction" in state["forecast_result"]:
                state["response"] += f"- Forecast: {state['forecast_result'].get('trend_direction')} trend with {state['forecast_result'].get('confidence_level')} confidence.\n"

        state["processing_time_ms"] = int((time.time() - start) * 1000)
        return state

    def _format_result(self, results: list) -> str:
        if not results:
            return "No data retrieved."
        if len(results) > 10:
            return json.dumps(results[:10], indent=2, default=str) + f"\n... and {len(results) - 10} more records"
        return json.dumps(results, indent=2, default=str)

    def _fallback_response(self, state: AgentState) -> str:
        parts = [f"Based on the analysis of your query: **{state['query']}**\n"]

        if state.get("sql_result"):
            parts.append(f"- Found {len(state['sql_result'])} relevant records in the database.")
        if state.get("graph_result"):
            parts.append(f"- Discovered {len(state['graph_result'])} relationships in the crime network.")
        if state.get("rag_result"):
            parts.append(f"- Retrieved {len(state['rag_result'])} similar cases from the knowledge base.")
        if state.get("analytics_result"):
            parts.append("- Pattern analysis completed.")
        if state.get("profiling_result"):
            p = state["profiling_result"]
            parts.append(f"- Offender profile: {p.get('archetype', 'N/A')} — Risk: {p.get('risk_level', 'N/A')}")
        if state.get("forecast_result"):
            f = state["forecast_result"]
            parts.append(f"- Forecast: {f.get('trend_direction', 'stable')} trend with {f.get('confidence_level', 'N/A')} confidence.")

        return "\n".join(parts)
