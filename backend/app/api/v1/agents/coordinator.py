import json
import time
from typing import List
from app.core.config import settings
from app.services.openai_client import create_openai_client
from app.llm.state import AgentState, IntentType

client = create_openai_client()

INTENT_CLASSIFICATION_PROMPT = """
You are the Coordinator Agent for Sentinel AI, a law enforcement intelligence platform.

Analyze the user's query and classify the intent into EXACTLY ONE category:

- sql_query: Questions about specific records, statistics, case details, filtering, counts, person search
- graph_query: Network relationships, connections between entities, gang structures, hidden links
- rag_search: Similar cases, semantic search, precedent matching across documents
- analytics: Crime trends, patterns, hotspots, sociological insights, temporal analysis
- profile: Offender risk scoring, behavioral analysis, archetype classification, modus operandi
- forecast: Predictions, future crime patterns, early warnings, crime volume forecasting
- general: Greetings, help, system information, unclear questions, chitchat

User Query: {query}

Conversation Context: {context}

Respond with ONLY a JSON object:
{{"intent": "category", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}
"""


class CoordinatorAgent:
    async def run(self, state: AgentState) -> AgentState:
        start = time.time()
        context_summary = self._summarize_context(state.get("context", []))

        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": INTENT_CLASSIFICATION_PROMPT.format(
                        query=state["query"], context=context_summary
                    )},
                    {"role": "user", "content": state["query"]},
                ],
                temperature=0.1,
                max_tokens=150,
            )

            raw = response.choices[0].message.content.strip()
            # Handle markdown-wrapped JSON
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            result = json.loads(raw)
            intent_str = result.get("intent", "general")
            state["intent"] = IntentType(intent_str)
            state["intent_confidence"] = float(result.get("confidence", 0.8))
            state["intent_reasoning"] = result.get("reasoning", "")
            state["reasoning_chain"].append(
                f"Coordinator classified intent as '{intent_str}' (confidence: {state['intent_confidence']:.2f})"
            )
        except Exception as e:
            state["intent"] = IntentType.GENERAL
            state["intent_confidence"] = 0.5
            state["intent_reasoning"] = f"Fallback due to error: {str(e)}"
            state["reasoning_chain"].append(f"Coordinator fallback: {str(e)}")

        state["processing_time_ms"] = int((time.time() - start) * 1000)
        return state

    def _summarize_context(self, context: List[dict]) -> str:
        if not context:
            return "No previous conversation context."
        recent = context[-3:]
        return " | ".join([f"{c.get('role', 'user')}: {c.get('content', '')[:100]}" for c in recent])
