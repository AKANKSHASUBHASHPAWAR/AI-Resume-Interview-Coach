import re
import io
import PyPDF2
from docx import Document


def clean_extracted_text(text):
    """
    Cleans raw extracted text:
    - Normalizes null bytes and unicode artifacts
    - Replaces non-breaking spaces
    - Standardizes carriage returns
    - Collapses excessive blank lines
    """
    if not text:
        return ""

    # Remove null bytes
    text = text.replace("\x00", "")
    # Normalize non-breaking spaces and line separators
    text = text.replace("\xa0", " ").replace("\r\n", "\n").replace("\r", "\n")
    # Replace weird PDF ligatures if any
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")
    # Collapse 3+ consecutive newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespaces
    return text.strip()


def extract_pdf(file):
    """
    Extracts text from PDF files using PyPDF2 with page separation,
    graceful error handling, and text normalization.
    """
    try:
        if hasattr(file, "seek"):
            file.seek(0)
        reader = PyPDF2.PdfReader(file)
        pages_text = []

        for page_idx, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    pages_text.append(page_text.strip())
            except Exception:
                continue

        full_text = "\n\n".join(pages_text)
        return clean_extracted_text(full_text)
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"


def extract_docx(file):
    """
    Extracts text from DOCX files including paragraphs, tables,
    and headers/footers with structural layout preservation.
    """
    try:
        if hasattr(file, "seek"):
            file.seek(0)
        doc = Document(file)
        text_parts = []

        # 1. Check Header
        try:
            for section in doc.sections:
                header = section.header
                for p in header.paragraphs:
                    if p.text.strip():
                        text_parts.append(p.text.strip())
        except Exception:
            pass

        # 2. Main Paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text.strip())

        # 3. Tables (crucial for multi-column resumes)
        for table in doc.tables:
            for row in table.rows:
                cells_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                # Deduplicate identical adjacent cells (due to merged cells)
                unique_cells = []
                for c in cells_text:
                    if not unique_cells or c != unique_cells[-1]:
                        unique_cells.append(c)
                if unique_cells:
                    text_parts.append(" | ".join(unique_cells))

        full_text = "\n\n".join(text_parts)
        return clean_extracted_text(full_text)
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"


def extract_txt(file):
    """
    Extracts text from TXT or Markdown files.
    """
    try:
        if isinstance(file, str):
            return clean_extracted_text(file)
        elif hasattr(file, "read"):
            if hasattr(file, "seek"):
                file.seek(0)
            content = file.read()
            if isinstance(content, bytes):
                return clean_extracted_text(content.decode("utf-8", errors="ignore"))
            return clean_extracted_text(str(content))
        return ""
    except Exception as e:
        return f"Error reading text file: {str(e)}"