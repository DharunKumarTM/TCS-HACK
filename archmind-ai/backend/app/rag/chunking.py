import re
from typing import List, Dict, Any

class SemanticChunker:
    """
    Splits document text into semantically cohesive chunks preserving headings,
    page boundaries, and bullet lists with configurable overlap.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, document_id: str, filename: str) -> List[Dict[str, Any]]:
        """
        Splits text into chunks by paragraphs and sentences.
        """
        if not text or not text.strip():
            return []

        # Split by double newlines or section markers first
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chunks = []
        current_chunk_words: List[str] = []
        current_page = 1
        chunk_index = 0

        for para in paragraphs:
            # Check for page markers
            page_match = re.search(r"---\s*Page\s*(\d+)\s*---", para, re.IGNORECASE)
            if page_match:
                current_page = int(page_match.group(1))

            words = para.split()
            if not words:
                continue

            if len(current_chunk_words) + len(words) <= self.chunk_size:
                current_chunk_words.extend(words)
            else:
                # If current chunk has content, finalize it
                if current_chunk_words:
                    chunk_text = " ".join(current_chunk_words)
                    chunks.append({
                        "document_id": document_id,
                        "chunk_index": chunk_index,
                        "filename": filename,
                        "content": chunk_text,
                        "token_count": len(current_chunk_words),
                        "page_number": current_page
                    })
                    chunk_index += 1

                    # Retain overlap words
                    overlap_count = min(self.chunk_overlap, len(current_chunk_words))
                    current_chunk_words = current_chunk_words[-overlap_count:] + words
                else:
                    # Single very large paragraph, slice into sub-chunks
                    for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
                        sub_words = words[i:i + self.chunk_size]
                        chunks.append({
                            "document_id": document_id,
                            "chunk_index": chunk_index,
                            "filename": filename,
                            "content": " ".join(sub_words),
                            "token_count": len(sub_words),
                            "page_number": current_page
                        })
                        chunk_index += 1
                    current_chunk_words = []

        if current_chunk_words:
            chunks.append({
                "document_id": document_id,
                "chunk_index": chunk_index,
                "filename": filename,
                "content": " ".join(current_chunk_words),
                "token_count": len(current_chunk_words),
                "page_number": current_page
            })

        return chunks

semantic_chunker = SemanticChunker()

