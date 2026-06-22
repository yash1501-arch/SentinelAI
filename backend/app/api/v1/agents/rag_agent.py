import time
from app.llm.state import AgentState
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


RAG_COLLECTION_MAP = {
    "crime": "crime_descriptions",
    "fir": "fir_text",
    "case": "case_notes",
    "witness": "witness_statements",
    "evidence": "evidence_descriptions",
}


class RAGAgent:
    async def run(self, state: AgentState) -> AgentState:
        start = time.time()

        try:
            query = state["query"]
            state["rag_query"] = query

            query_vector = EmbeddingService.embed_query(query)

            all_results = []
            collections_to_search = self._select_collections(query)

            for collection in collections_to_search:
                results = await QdrantService.search_similar(
                    collection=collection,
                    query_vector=query_vector,
                    top_k=5,
                    score_threshold=0.65,
                )
                all_results.extend(results)

            all_results.sort(key=lambda x: x["score"], reverse=True)
            state["rag_result"] = all_results[:10]
            state["reasoning_chain"].append(
                f"RAG Agent searched {len(collections_to_search)} collections, found {len(all_results)} relevant documents"
            )

        except Exception as e:
            state["rag_error"] = str(e)
            state["rag_result"] = []
            state["reasoning_chain"].append(f"RAG Agent error: {str(e)}")

        state["processing_time_ms"] = int((time.time() - start) * 1000)
        return state

    def _select_collections(self, query: str) -> list:
        query_lower = query.lower()
        collections = ["crime_descriptions", "fir_text"]

        if any(w in query_lower for w in ["witness", "statement", "testimony", "said"]):
            collections.append("witness_statements")
        if any(w in query_lower for w in ["evidence", "forensic", "cctv", "digital"]):
            collections.append("evidence_descriptions")
        if any(w in query_lower for w in ["case note", "investigation", "progress", "update"]):
            collections.append("case_notes")
        if any(w in query_lower for w in ["similar", "like", "precedent", "comparable"]):
            collections.extend(["crime_descriptions", "fir_text", "case_notes"])

        return list(set(collections))
