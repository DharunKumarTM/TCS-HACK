import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import DocumentChunk, Evidence
from app.rag.embeddings import embedding_service

logger = logging.getLogger("archmind.rag.retriever")

class EvidenceRetriever:
    """
    Retrieves grounded evidence from stored document chunks and extracted evidence
    using semantic vector similarity and keyword filtering.
    """

    def retrieve_relevant_chunks(
        self,
        db: Session,
        query: str,
        project_id: str,
        top_k: int = 5,
        threshold: float = 0.25
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top_k relevant document chunks for the given query.
        """
        query_vec = embedding_service.get_embedding(query)

        # Query all chunks for documents belonging to this project
        from app.database.models import Document
        chunks = (
            db.query(DocumentChunk)
            .join(Document, DocumentChunk.document_id == Document.id)
            .filter(Document.project_id == project_id)
            .all()
        )

        scored_chunks = []
        query_words = set(query.lower().split())

        for chunk in chunks:
            sim = 0.0
            if chunk.embedding:
                sim = embedding_service.cosine_similarity(query_vec, chunk.embedding)
            else:
                # Calculate on the fly if chunk didn't have saved embedding
                chunk_vec = embedding_service.get_embedding(chunk.content)
                sim = embedding_service.cosine_similarity(query_vec, chunk_vec)

            # Keyword lexical bonus
            content_words = set(chunk.content.lower().split())
            overlap = len(query_words.intersection(content_words)) / max(1, len(query_words))
            combined_score = (0.75 * sim) + (0.25 * overlap)

            if combined_score >= threshold:
                scored_chunks.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "filename": chunk.document.filename if chunk.document else "Unknown",
                    "content": chunk.content,
                    "page_number": chunk.page_number,
                    "score": round(combined_score, 4)
                })

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

    def retrieve_grounded_evidence(
        self,
        db: Session,
        query: str,
        project_id: str,
        top_k: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Retrieves evidence items matching the query semantically.
        """
        query_vec = embedding_service.get_embedding(query)
        evidence_items = (
            db.query(Evidence)
            .filter(Evidence.project_id == project_id)
            .all()
        )

        scored_evidence = []
        for ev in evidence_items:
            ev_text = f"{ev.statement} {ev.original_excerpt} {ev.category}"
            ev_vec = embedding_service.get_embedding(ev_text)
            sim = embedding_service.cosine_similarity(query_vec, ev_vec)

            scored_evidence.append({
                "id": ev.id,
                "evidence_code": ev.evidence_code,
                "statement": ev.statement,
                "original_excerpt": ev.original_excerpt,
                "category": ev.category,
                "source_filename": ev.source_filename,
                "location_reference": ev.location_reference,
                "confidence_score": ev.confidence_score,
                "similarity_score": round(sim, 4)
            })

        scored_evidence.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_evidence[:top_k]

evidence_retriever = EvidenceRetriever()

