import os
import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("archmind.rag.parser")

class DocumentParser:
    """
    Parses PDF, DOCX, TXT, and Markdown documents using Docling with fast local fallbacks.
    Preserves document structure, section headers, and stakeholder statements.
    """

    def __init__(self):
        self._converter = None
        self._docling_attempted = False

    def _get_converter(self):
        if not self._docling_attempted:
            self._docling_attempted = True
            try:
                from docling.document_converter import DocumentConverter
                self._converter = DocumentConverter()
                logger.info("Docling DocumentConverter initialized lazily.")
            except Exception as e:
                logger.info(f"Docling using fast local parser fallback: {e}")
                self._converter = None
        return self._converter

    def parse_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Parses document file and returns extracted text, metadata, and structural sections.
        """
        ext = os.path.splitext(filename)[1].lower()
        text_content = ""

        # For text, markdown, and json, read directly (fastest and cleanest)
        if ext in [".txt", ".md", ".json"]:
            text_content = self._fallback_parse(file_path, ext)
        elif ext in [".pdf", ".docx"]:
            converter = self._get_converter()
            if converter:
                try:
                    result = converter.convert(file_path)
                    text_content = result.document.export_to_markdown()
                    logger.info(f"Parsed {filename} using Docling ({len(text_content)} chars)")
                except Exception as e:
                    logger.warning(f"Docling conversion failed for {filename}: {e}. Using fallback parser.")
                    text_content = self._fallback_parse(file_path, ext)
            else:
                text_content = self._fallback_parse(file_path, ext)
        else:
            text_content = self._fallback_parse(file_path, ext)

        sections = self._extract_sections(text_content)
        stakeholder_quotes = self._extract_stakeholder_quotes(text_content)

        return {
            "filename": filename,
            "file_type": ext.replace(".", ""),
            "raw_text": text_content,
            "sections": sections,
            "stakeholder_quotes": stakeholder_quotes,
            "character_count": len(text_content)
        }

    def _fallback_parse(self, file_path: str, ext: str) -> str:
        """Fallback parser using standard python libraries."""
        if ext in [".txt", ".md", ".json"]:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()

        if ext == ".pdf":
            try:
                import fitz  # pymupdf
                doc = fitz.open(file_path)
                text = ""
                for page_num in range(len(doc)):
                    text += f"\n--- Page {page_num + 1} ---\n" + doc[page_num].get_text()
                return text
            except Exception as e:
                logger.warning(f"PyMuPDF failed: {e}. Reading raw.")
                with open(file_path, "r", encoding="latin-1", errors="replace") as f:
                    return f.read()

        if ext == ".docx":
            try:
                import docx
                doc = docx.Document(file_path)
                return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            except Exception as e:
                logger.warning(f"python-docx failed: {e}")
                with open(file_path, "r", encoding="latin-1", errors="replace") as f:
                    return f.read()

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def _extract_sections(self, text: str) -> List[Dict[str, str]]:
        """Extracts markdown or plaintext sections based on headings."""
        sections = []
        lines = text.split("\n")
        current_header = "General"
        current_lines = []

        for line in lines:
            header_match = re.match(r"^(#{1,4}\s+|SECTION\s+\d+:?\s*|[0-9]+\.[0-9]*\s+)(.+)$", line, re.IGNORECASE)
            if header_match:
                if current_lines:
                    sections.append({
                        "header": current_header.strip(),
                        "content": "\n".join(current_lines).strip()
                    })
                    current_lines = []
                current_header = header_match.group(2).strip()
            else:
                current_lines.append(line)

        if current_lines:
            sections.append({
                "header": current_header.strip(),
                "content": "\n".join(current_lines).strip()
            })

        return sections

    def _extract_stakeholder_quotes(self, text: str) -> List[Dict[str, str]]:
        """Identifies stakeholder statements."""
        quotes = []
        pattern = re.compile(
            r"(?:([A-Z][A-Za-z0-9\s,\.\-]{3,40}?)\s*(?:\((?:VP|Director|Architect|Lead|Chief|Officer|Manager|Product|Compliance|Security|SRE|DevOps)[^\)]*\))?\s*[:\-\u2014]\s*[\"']?([^\"\n\r]+?[\"']?(?:\.|\n|$)))",
            re.IGNORECASE
        )
        for match in pattern.finditer(text):
            speaker = match.group(1).strip()
            statement = match.group(2).strip()
            if len(statement) > 15 and len(speaker) > 2:
                quotes.append({"speaker": speaker, "statement": statement})
        return quotes

document_parser = DocumentParser()
