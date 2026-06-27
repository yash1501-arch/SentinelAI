import time
import json
from app.core.config import settings
from app.services.openai_client import create_openai_client
from app.llm.state import AgentState, IntentType

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
                        analytics_result=json.dumps(state.get("analytics_result", {}), indent=2)[:2000],
                        profiling_result=json.dumps(state.get("profiling_result", {}), indent=2)[:2000],
                        forecast_result=json.dumps(state.get("forecast_result", {}), indent=2)[:2000],
                        reasoning_chain="\n".join(state.get("reasoning_chain", [])),
                        language=state.get("language", "English"),
                    )},
                ],
                temperature=0.3,
                max_tokens=1000,
            )

            raw = response.choices[0].message.content.strip()
            # Handle markdown-wrapped JSON
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            result = json.loads(raw)
            state["response"] = result.get("response", "")
            state["sources"] = result.get("sources", [])
            state["confidence_score"] = float(result.get("confidence_score", 0.5))
            state["reasoning_chain"].append(f"Summarizer generated final response")

            follow_ups = result.get("suggested_questions", [])
            if follow_ups:
                state["response"] += "\n\n**Suggested follow-ups:**\n" + "\n".join(
                    [f"- {q}" for q in follow_ups[:3]]
                )

        except Exception as e:
            state["response"] = self._fallback_response(state)
            state["confidence_score"] = 0.5
            state["reasoning_chain"].append(f"Summarizer fallback: {str(e)}")

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
