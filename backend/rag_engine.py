"""
TrendPulse — RAG Engine
ChromaDB vector store + SentenceTransformer embeddings + Groq LLM generation.
"""
import re
import chromadb
from groq import Groq
from typing import List

from backend.config import settings
from backend.models import TrendItem, RetrievedPassage, GeneratedContent


chroma_client = chromadb.Client()
_collection = None


def _get_collection():
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
            ids.append(f"trend_{i}_{trend.source.replace(' ', '_').replace('/', '_').lower()}")

    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)

    return len(documents)


def retrieve_relevant(query: str = "current trending topics in technology", top_k: int = 5) -> List[RetrievedPassage]:
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
            similarity_score=round(similarity, 4),
        ))

    passages.sort(key=lambda p: p.similarity_score, reverse=True)
    return passages


def _build_rag_prompt(passages: List[RetrievedPassage]) -> str:
    context_lines = []
    for i, p in enumerate(passages):
        source_badge = {"news": "News", "social_chatter": "Social", "emerging_topic": "Emerging"}.get(p.source_type, "Other")
        context_lines.append(
            f"[{i + 1}] ({source_badge}) {p.source}\n"
            f"    Title: {p.title}\n"
            f"    Content: {p.text[:400]}\n"
            f"    URL: {p.url}"
        )
    context_block = "\n\n".join(context_lines)

    return f"""You are TrendPulse, an AI trend summarizer. Write ONE Reddit post grounded ONLY in the sources below. Never invent facts. Do NOT include any thinking, reasoning, or chain-of-thought. Output ONLY the formatted post.

SOURCES:
{context_block}

Write a Reddit post summarizing today's top tech trends. Use this EXACT format:

TITLE: <your title here>
BODY: <3-4 paragraphs referencing sources as [1], [2] etc.>
SOURCES: <comma separated source numbers used, e.g. 1, 2, 3>
HASHTAGS: <3 hashtags>"""


def _strip_thinking_tags(text: str) -> str:
    """Remove <think>...</think> tags from model output (Qwen produces these)."""
    # Complete tags
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Unclosed tag — strip from <think> to right before TITLE:/BODY: keywords
    cleaned = re.sub(r'<think>.*?(?=TITLE:|BODY:|$)', '', cleaned, flags=re.DOTALL)
    return cleaned.strip()


def generate_content(passages: List[RetrievedPassage]) -> GeneratedContent:
    if not passages:
        return GeneratedContent(
            title="No trend data available",
            body="The pipeline fetched trends but no passages were retrieved from ChromaDB. Try running again.",
            retrieved_passages=[],
            model="none",
        )

    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY.startswith("your_"):
        return GeneratedContent(
            title="[ERROR] Groq API key not configured",
            body="Set GROQ_API_KEY in .env",
            retrieved_passages=passages,
        )

    client = Groq(api_key=settings.GROQ_API_KEY)
    prompt = _build_rag_prompt(passages)

    # Preferred model order — compound gives best results
    preferred_models = [
        "groq/compound",
        "qwen/qwen3.6-27b",
        "openai/gpt-oss-120b",
        "groq/compound-mini",
        "openai/gpt-oss-20b",
    ]

    # Also query available models in case our list is stale
    try:
        models_resp = client.models.list()
        available_ids = set()
        for m in models_resp.data:
            mid = m.id
            if any(skip in mid for skip in ["whisper", "guard", "orpheus", "safeguard", "allam"]):
                continue
            available_ids.add(mid)

        # Use preferred order but only include models that are actually available
        candidate_models = [m for m in preferred_models if m in available_ids]
        # Add any available models not in our preferred list
        for mid in available_ids:
            if mid not in candidate_models:
                candidate_models.append(mid)
    except Exception:
        candidate_models = preferred_models

    completion = None
    used_model = "unknown"
    last_error = None

    for model_name in candidate_models:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500,
            )
            response_text = completion.choices[0].message.content or ""

            # Strip thinking tags and check if we got real content
            response_text = _strip_thinking_tags(response_text)
            if len(response_text.strip()) > 30:
                used_model = model_name
                break
            else:
                last_error = f"{model_name} returned too short response"
                completion = None
                continue
        except Exception as e:
            last_error = str(e)[:200]
            completion = None
            continue

    if not completion:
        return GeneratedContent(
            title="[ERROR] Content generation failed",
            body=f"All Groq models failed. Last error: {last_error}",
            retrieved_passages=passages,
            model="error",
        )

    response_text = _strip_thinking_tags(completion.choices[0].message.content or "")

    # Parse structured response
    title = ""
    body = ""
    citations = []
    hashtags = ""
    current_section = None

    for line in response_text.split("\n"):
        stripped = line.strip()
        up = stripped.upper()

        if up.startswith("TITLE:"):
            current_section = "title"
            title = stripped[6:].strip()
        elif up.startswith("BODY:"):
            current_section = "body"
            body = stripped[5:].strip()
        elif up.startswith("SOURCES:"):
            current_section = "sources"
            citations = [int(x) for x in re.findall(r'\d+', stripped)]
        elif up.startswith("HASHTAG"):
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
    vectors_indexed = ingest_trends(trends)
    passages = retrieve_relevant(query=query, top_k=5)
    content = generate_content(passages)
    return vectors_indexed, passages, content
