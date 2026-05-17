"""Document processing service for PDF and DOCX extraction."""

import os
import re
from pathlib import Path
from typing import Tuple, List, Optional
from docx import Document as DocxDocument
import PyPDF2


class DocumentProcessor:
    """Process contracts in various formats."""

    @staticmethod
    def extract_from_docx(file_path: str) -> Tuple[str, dict]:
        """
        Extract text from DOCX file.

        Returns:
            (extracted_text, metadata)
        """
        try:
            doc = DocxDocument(file_path)
            text_parts = []

            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)

            # Extract from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text_parts.append(cell.text)

            text = '\n'.join(text_parts)

            metadata = {
                "file_type": "docx",
                "num_paragraphs": len(doc.paragraphs),
                "num_tables": len(doc.tables),
                "character_count": len(text),
            }

            return text, metadata

        except Exception as e:
            raise Exception(f"Failed to extract DOCX: {str(e)}")

    @staticmethod
    def extract_from_pdf(file_path: str) -> Tuple[str, dict]:
        """
        Extract text from PDF file.

        Returns:
            (extracted_text, metadata)
        """
        try:
            text_parts = []
            num_pages = 0

            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)

                for page in reader.pages:
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(text)

            text = '\n'.join(text_parts)

            metadata = {
                "file_type": "pdf",
                "num_pages": num_pages,
                "character_count": len(text),
            }

            return text, metadata

        except Exception as e:
            raise Exception(f"Failed to extract PDF: {str(e)}")

    @staticmethod
    def process_document(file_path: str) -> Tuple[str, dict]:
        """
        Extract text and metadata from PDF or DOCX.

        Args:
            file_path: Path to document file

        Returns:
            Tuple of (extracted_text, metadata)
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_ext = path.suffix.lower()

        if file_ext == '.docx':
            return DocumentProcessor.extract_from_docx(file_path)
        elif file_ext == '.pdf':
            return DocumentProcessor.extract_from_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    @staticmethod
    def extract_clauses(text: str) -> List[dict]:
        """
        Extract clause-like sections from contract text.

        Simple heuristic: split by "Article", "Section", "Clause" headers.

        Returns:
            List of clause dicts with text and metadata
        """

        clauses = []
        clause_id = 0

        # Split by common clause patterns
        patterns = [
            (r'(Article|Article\s+\d+\s*[:\.].*?)(?=Article|\Z)', 'Article'),
            (r'(Section|Section\s+\d+\s*[:\.].*?)(?=Section|\Z)', 'Section'),
            (r'(Clause|Clause\s+\d+\s*[:\.].*?)(?=Clause|\Z)', 'Clause'),
        ]

        for pattern, clause_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                clause_text = match.group(1).strip()
                if len(clause_text) > 20:
                    clause_id += 1
                    clauses.append({
                        "id": f"CLAUSE_{clause_id:03d}",
                        "type": clause_type,
                        "content": clause_text[:1000],  # Limit size
                        "full_content": clause_text,
                    })

        return clauses

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize document text for processing.

        - Remove extra whitespace
        - Standardize line endings
        - Remove control characters
        """

        # Remove control characters but keep newlines
        text = ''.join(c for c in text if ord(c) >= 32 or c in '\n\t\r')

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r' +\n', '\n', text)
        text = re.sub(r'\n+', '\n', text)

        return text.strip()
