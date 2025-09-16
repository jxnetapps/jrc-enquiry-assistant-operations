import io
import os
from typing import List, Dict

from pypdf import PdfReader
from docx import Document as DocxDocument


def parse_pdf(file_bytes: bytes, filename: str) -> Dict[str, str]:
    reader = PdfReader(io.BytesIO(file_bytes))
    texts: List[str] = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            continue
    content = "\n".join(texts)
    title = os.path.splitext(os.path.basename(filename))[0]
    return {"title": title, "content": content}


def parse_docx(file_bytes: bytes, filename: str) -> Dict[str, str]:
    doc = DocxDocument(io.BytesIO(file_bytes))
    texts: List[str] = [p.text for p in doc.paragraphs if p.text]
    content = "\n".join(texts)
    title = os.path.splitext(os.path.basename(filename))[0]
    return {"title": title, "content": content}


def parse_txt(file_bytes: bytes, filename: str) -> Dict[str, str]:
    content = file_bytes.decode("utf-8", errors="ignore")
    title = os.path.splitext(os.path.basename(filename))[0]
    return {"title": title, "content": content}


