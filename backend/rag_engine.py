"""
TrendPulse — RAG Engine
ChromaDB vector store + SentenceTransformer embeddings + Groq LLM generation.
This is the core RAG pipeline: Ingest → Embed → Retrieve → Generate.
"""
import chromadb
from groq import Groq
from typing import List

from backend.config import settings
from backend.models import TrendItem, RetrievedPassage, GeneratedContent


# Initialize ChromaDB in-memory client
chroma_client = chromadb.Client()

_collection = None


def _get_collection():
    """Get or create the trends collection with SentenceTransformer embeddings."""
    global _collection
    if _collection is None:
        try:
            from chromadb.utils import embedding_functions
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            _collection = chroma_client.get_or_create_collection(
                name="trendpulse_trends",
                embedding_function=ef,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception:
            _collection = chroma_client.get_or_create_collection(
                name="trendpulse_trends",
                metadata={"hnsw:space": "cosine"},
            )
    return _collection


def ingest_trends(trends: List[TrendItem]) -> int:
    """
    Ingest trend documents into ChromaDB vector store.
    Each trend is chunked, embedded, and indexed with source metadata.
    """
    collection = _get_collection()

    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    if not trends:
        return 0

    documents = []
    metadatas = []
    ids = []

    for i, trend in enumerate(trends):
        doc_text = trend.to_document()
        if doc_text.strip():
            documents.append(doc_text)
            metadatas.append(trend.to_metadata())
            ids.append(f"trend_{i}_{trend.source.replace(' ', '_').lower()}")

    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    return len(documents)


def retrieve_relevant(query: str = "current trending topics in technology", top_k: int = 5) -> List[RetrievedPassage]:
    """
    Retrieve the top-K most relevant trend passages from ChromaDB
    using cosine similarity vector search.
    """
    collection = _get_collection()

    count = collection.count()
    if count == 0:
        return []

    n_results = min(top_k, count)

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    passages = []
    for i in range(len(results["documents"][0])):
        distance = results["distances"][0][i]
        similarity = 1.0 - (distance / 2.0)

        metadata = results["metadatas"][0][i]
        passages.append(RetrievedPassage(
            text=results["documents"][0][i],
            source=metadata.get("source", "Unknown"),
            source_type=metadata.get("source_type", "unknown"),
            url=metadata.get("url", ""),
            title=metadata.get("title", ""),
            similarity_score=similarity,
        ))

    passages.sort(key=lambda p: p.similarity_score, reverse=True)
    return passages


def _build_rag_prompt(passages: List[RetrievedPassage]) -> str:
    """Build the RAG-grounded prompt with retrieved context."""
    context_lines = []
    for i, p in enumerate(passages):
        source_badge = {
            "news": "News",
            "social_chatter": "Social Chatter",
            "emerging_topic": "Emerging Topic",
        }.get(p.source_type, "Other")

        context_lines.append(
            f"[{i + 1}] SOURCE: {p.source} | TYPE: {source_badge}\n"
            f"    TITLE: {p.title}\n"
            f"    CONTENT: {p.text}\n"
            f"    URL: {p.url}"
        )

    context_block = "\n\n".join(context_lines)

    return f"""You are TrendPulse, an AI content engine. Generate ONE Reddit post STRICTLY grounded in the retrieved trend documents below. Never invent facts, statistics, or claims not present in the sources.

RETRIEVED TREND CONTEXT (Top-{len(passages)} by vector similarity):
---
{context_block}
---

TASK: Write a Reddit post for r/test that summarizes today's top trending topics.

FORMAT YOUR RESPONSE EXACTLY AS:
TITLE: [One clear, engaging title — max 300 chars]
BODY: [3-4 paragraphs grounded in above sources. Reference sources as [1], [2], etc.]
SOURCES: [List which source numbers you used, e.g. 1, 2, 3]
HASHTAGS: [3 relevant hashtags]

Generate now:"""


def generate_content(passages: List[RetrievedPassage]) -> GeneratedContent:
    """
    Generate grounded content using Groq LLM with retrieved RAG passages.
    Tries models in order: llama-3.3-70b-versatile, llama3-70b-8192, llama-3.1-70b-versatile, mixtral-8x7b-32768.
    """
    if not settings.GROQ_API_KEY:
        return GeneratedContent(
            title="[ERROR] Groq API key not configured",
            body="Please set GROQ_API_KEY in your .env file.",
            retrieved_passages=passages,
        )

    client = Groq(api_key=settings.GROQ_API_KEY)
    prompt = _build_rag_prompt(passages)

    # List of candidate Groq models
    candidate_models = [
        "llama-3.3-70b-versatile",
        "llama3-70b-8192",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768",
        "llama3-8b-8192"
    ]

    completion = None
    used_model = candidate_models[0]
    last_error = None

    for model_name in candidate_models:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
            )
            used_model = model_name
            break
        except Exception as e:
            last_error = str(e)
            continue

    if not completion:
        return GeneratedContent(
            title="[ERROR] Content generation failed",
            body=f"Groq API error across all models: {last_error}",
            retrieved_passages=passages,
        )

    response_text = completion.choices[0].message.content

    # Parse the structured response
    title = ""
    body = ""
    citations = []
    hashtags = ""

    lines = response_text.split("\n")
    current_section = None

    for line in lines:
        stripped = line.strip()
        if stripped.upper().startswith("TITLE:"):
            current_section = "title"
            title = stripped[6:].strip()
        elif stripped.upper().startswith("BODY:"):
            current_section = "body"
            body = stripped[5:].strip()
        elif stripped.upper().startswith("SOURCES:"):
            current_section = "sources"
            sources_str = stripped[8:].strip()
            import re
            citations = [int(x) for x in re.findall(r'\d+', sources_str)]
        elif stripped.upper().startswith("HASHTAGS:") or stripped.upper().startswith("HASHTAG:"):
            current_section = "hashtags"
            hashtags = stripped.split(":", 1)[1].strip() if ":" in stripped else ""
        elif current_section == "body" and stripped:
            body += "\n" + stripped
        elif current_section == "title" and stripped and not title:
            title = stripped

    body = body.strip()
    if hashtags:
        body += f"\n\n{hashtags}"

    if not title:
        title = "Today's Top Trending Topics in Technology"
    if not body:
        body = response_text

    return GeneratedContent(
        title=title,
        body=body,
        citations=citations,
        retrieval_scores=[p.similarity_score for p in passages],
        retrieved_passages=passages,
        model=used_model,
    )


def run_rag_pipeline(trends: List[TrendItem], query: str = "current trending topics in technology") -> tuple:
    """
    Full RAG pipeline: Ingest → Retrieve → Generate.
    """
    vectors_indexed = ingest_trends(trends)
    passages = retrieve_relevant(query=query, top_k=5)
    content = generate_content(passages)
    return vectors_indexed, passages, content
