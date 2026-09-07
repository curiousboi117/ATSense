import io
import os
import fitz  # PyMuPDF
import docx
from typing import Dict, Any

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def parse_file(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    Parses a PDF or DOCX file content and returns extracted text, page count, and metadata.
    """
    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError("File size exceeds the maximum limit of 5MB.")
    
    if not file_content:
        raise ValueError("The uploaded file is empty.")

    ext = os.path.splitext(filename.lower())[1]
    
    if ext == ".pdf":
        return parse_pdf(file_content)
    elif ext == ".docx":
        return parse_docx(file_content)
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX files are allowed.")

def parse_pdf(file_content: bytes) -> Dict[str, Any]:
    """
    Extracts text from PDF file content using PyMuPDF.
    """
    try:
        doc = fitz.open(stream=file_content, filetype="pdf")
        text_parts = []
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text_parts.append(page_text)
        
        text = "\n".join(text_parts)
        if not text.strip():
            raise ValueError("No text could be extracted from this PDF. It might be scanned or empty.")
            
        return {
            "text": text,
            "page_count": len(doc),
            "metadata": doc.metadata or {}
        }
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise ValueError(f"Failed to parse PDF file: {str(e)}")

def parse_docx(file_content: bytes) -> Dict[str, Any]:
    """
    Extracts text from DOCX file content using python-docx.
    """
    try:
        doc_stream = io.BytesIO(file_content)
        doc = docx.Document(doc_stream)
        
        text_parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)
                
        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text_parts.append(cell.text)
                        
        text = "\n".join(text_parts)
        if not text.strip():
            raise ValueError("No text could be extracted from this DOCX file.")
            
        metadata = {}
        try:
            metadata = {
                "author": doc.core_properties.author or "",
                "title": doc.core_properties.title or "",
                "created": str(doc.core_properties.created) if doc.core_properties.created else ""
            }
        except Exception:
            pass
            
        return {
            "text": text,
            "page_count": None,  # Word documents do not have pages natively in docx format
            "metadata": metadata
        }
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise ValueError(f"Failed to parse DOCX file: {str(e)}")
