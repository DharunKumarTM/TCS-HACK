import math
import hashlib
import re
import logging
from typing import List
from app.config import settings

logger = logging.getLogger("archmind.rag.embeddings")

class EmbeddingService:
    """
    Generates dense vector embeddings.
    Uses Google GenAI / Gemini API if configured; falls back to an offline normalized
    feature hashing embedding engine with cosine compatibility.
    """

    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.client = None
        self._init_client()

    def _init_client(self):
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here":
            try:
                from google import genai
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("Gemini Embedding client initialized.")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini Client: {e}")
                self.client = None

    def get_embedding(self, text: str) -> List[float]:
        """Returns a 768-dimensional normalized embedding vector for the text."""
        if not text or not text.strip():
            return [0.0] * self.dimension

        if self.client:
            try:
                # Use Gemini Embeddings
                response = self.client.models.embed_content(
                    model="text-embedding-004",
                    contents=text
                )
                if hasattr(response, "embedding") and response.embedding:
                    vec = response.embedding.values
                    # Normalize vector
                    norm = math.sqrt(sum(x * x for x in vec))
                    return [x / norm for x in vec] if norm > 0 else vec
            except Exception as e:
                logger.warning(f"Gemini API embed call failed: {e}. Falling back to deterministic embedding.")

        return self._deterministic_embedding(text)

    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self.get_embedding(t) for t in texts]

    def _deterministic_embedding(self, text: str) -> List[float]:
        """
        Generates a 768-dim semantic hash vector with token frequency weighting
        and positional decay, normalized for cosine similarity calculations.
        """
        vec = [0.0] * self.dimension
        words = re.findall(r"\w+", text.lower())
        if not words:
            return vec

        for idx, word in enumerate(words):
            # Primary word hash
            h1 = int(hashlib.md5(word.encode()).hexdigest(), 16) % self.dimension
            # Bigram hash if possible
            h2 = int(hashlib.sha256(word.encode()).hexdigest(), 16) % self.dimension
            
            weight = 1.0 / (1.0 + 0.05 * math.log(idx + 1))
            vec[h1] += 1.2 * weight
            vec[h2] += 0.8 * weight

        # Sub-word character trigrams for semantic robustness
        for i in range(len(text) - 2):
            tri = text[i:i+3].lower()
            h = int(hashlib.sha1(tri.encode()).hexdigest(), 16) % self.dimension
            vec[h] += 0.25

        # L2 Normalize
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [round(v / norm, 6) for v in vec]
        return vec

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        return max(0.0, min(1.0, dot))

embedding_service = EmbeddingService(dimension=settings.EMBEDDING_DIMENSION)

