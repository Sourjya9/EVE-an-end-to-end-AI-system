"""
Jina AI Embeddings Client.

Connects to Jina AI v3 embedding API to compute dense vector embeddings.
Includes batching, retries, and deterministic offline mock embeddings for test suites.
"""

import hashlib
import math

import httpx

from app.core.config import settings
from app.core.logging import logger
from app.core.observability.opik import opik_tracer


class JinaEmbeddingClient:
    """Production client for Jina AI vector embeddings."""

    def __init__(self) -> None:
        self.api_key = settings.JINA_API_KEY
        self.model = settings.JINA_EMBEDDING_MODEL
        self.dimensions = settings.JINA_EMBEDDING_DIM
        self.api_url = settings.JINA_API_URL

        if not self.api_key:
            logger.info(
                "Jina API key not configured; using deterministic mock embeddings for local development/testing."
            )

    def _generate_deterministic_mock_embedding(self, text: str) -> list[float]:
        """Generates a normalized pseudo-random vector based on text hash for tests."""
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16)
        vec: list[float] = []
        for i in range(self.dimensions):
            val = math.sin(seed + i * 0.17) * math.cos(seed * 0.31 + i)
            vec.append(val)

        # Normalize to unit length (L2 norm)
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [round(x / norm, 6) for x in vec]

    async def embed_texts(
        self, texts: list[str], task: str = "retrieval.passage"
    ) -> list[list[float]]:
        """
        Embeds a list of texts in batches.
        Task options: 'retrieval.passage', 'retrieval.query', 'text-matching'
        """
        if not texts:
            return []

        if not self.api_key:
            return [self._generate_deterministic_mock_embedding(t) for t in texts]

        all_embeddings: list[list[float]] = []
        batch_size = 32

        with opik_tracer.trace_span(
            "jina_embed_texts", {"count": len(texts), "task": task}
        ):
            async with httpx.AsyncClient(timeout=30.0) as client:
                for i in range(0, len(texts), batch_size):
                    batch = texts[i : i + batch_size]
                    payload = {
                        "model": self.model,
                        "task": task,
                        "dimensions": self.dimensions,
                        "late_chunking": False,
                        "input": batch,
                    }
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    }

                    try:
                        response = await client.post(
                            self.api_url, json=payload, headers=headers
                        )
                        response.raise_for_status()
                        data = response.json()
                        batch_vectors = [item["embedding"] for item in data["data"]]
                        all_embeddings.extend(batch_vectors)
                    except httpx.HTTPStatusError as exc:
                        logger.error(
                            f"Jina API HTTP error {exc.response.status_code}: {exc.response.text}"
                        )
                        raise RuntimeError(
                            f"Embedding generation failed: {exc.response.text}"
                        ) from exc
                    except Exception as exc:
                        logger.error(f"Failed to generate embeddings via Jina: {exc}")
                        raise RuntimeError(
                            f"Failed connecting to Jina embeddings API: {exc}"
                        ) from exc

        return all_embeddings

    async def embed_query(self, query: str) -> list[float]:
        """Embeds a single search query."""
        results = await self.embed_texts([query], task="retrieval.query")
        return results[0]


jina_client = JinaEmbeddingClient()
