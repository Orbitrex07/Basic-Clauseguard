import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import fitz  # PyMuPDF
import docx
from app.core.config import settings


@dataclass
class ParsedPage:
    page_number: int
    text: str


class DocumentParser:
    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        # Replace non-breaking spaces and tabs
        text = text.replace("\u00a0", " ").replace("\t", " ")
        # Normalize multiple spaces on a single line
        text = re.sub(r"[ ]{2,}", " ", text)
        # Normalize excessive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @classmethod
    def clean_headers_and_footers(cls, pages: List[ParsedPage]) -> List[ParsedPage]:
        if len(pages) < 2:
            return pages

        top_lines: Dict[str, int] = {}
        bottom_lines: Dict[str, int] = {}

        # Collect top and bottom lines per page
        for p in pages:
            lines = [line.strip() for line in p.text.split("\n") if line.strip()]
            if lines:
                top = lines[0]
                bottom = lines[-1]
                top_lines[top] = top_lines.get(top, 0) + 1
                bottom_lines[bottom] = bottom_lines.get(bottom, 0) + 1

        threshold = max(2, int(len(pages) * 0.5))
        repeated_top = {line for line, count in top_lines.items() if count >= threshold}
        repeated_bottom = {line for line, count in bottom_lines.items() if count >= threshold}

        cleaned_pages = []
        for p in pages:
            lines = [line.strip() for line in p.text.split("\n") if line.strip()]
            if not lines:
                cleaned_pages.append(p)
                continue

            filtered_lines = []
            for i, line in enumerate(lines):
                # Check top line
                if i == 0 and line in repeated_top:
                    continue
                # Check bottom line
                if i == len(lines) - 1 and line in repeated_bottom:
                    continue
                # Also strip standalone page numbers like "Page 1 of 5" or "1"
                if re.match(r"^(page\s+\d+(\s+of\s+\d+)?|\d+)$", line, re.IGNORECASE):
                    continue
                filtered_lines.append(line)

            cleaned_pages.append(ParsedPage(
                page_number=p.page_number,
                text=cls.normalize_text("\n".join(filtered_lines))
            ))

        return cleaned_pages

    @classmethod
    def parse_pdf(cls, file_path: str) -> List[ParsedPage]:
        doc = fitz.open(file_path)
        page_count = len(doc)
        if page_count > settings.MAX_PAGES:
            doc.close()
            raise ValueError(f"Document exceeds maximum allowed page count of {settings.MAX_PAGES} (found {page_count} pages)")

        pages: List[ParsedPage] = []
        for i in range(page_count):
            page = doc[i]
            text = page.get_text("text")
            pages.append(ParsedPage(
                page_number=i + 1,
                text=cls.normalize_text(text)
            ))
        doc.close()
        return cls.clean_headers_and_footers(pages)

    @classmethod
    def parse_docx(cls, file_path: str) -> List[ParsedPage]:
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        
        # In DOCX, estimate pages (~450 words or page break markers per page)
        pages: List[ParsedPage] = []
        current_page_lines: List[str] = []
        current_word_count = 0
        current_page_num = 1

        for para in paragraphs:
            words = len(para.split())
            if current_word_count + words > 450 and current_page_lines:
                pages.append(ParsedPage(
                    page_number=current_page_num,
                    text=cls.normalize_text("\n\n".join(current_page_lines))
                ))
                current_page_num += 1
                current_page_lines = [para]
                current_word_count = words
            else:
                current_page_lines.append(para)
                current_word_count += words

        if current_page_lines:
            pages.append(ParsedPage(
                page_number=current_page_num,
                text=cls.normalize_text("\n\n".join(current_page_lines))
            ))

        if len(pages) > settings.MAX_PAGES:
            raise ValueError(f"Document exceeds maximum allowed page count of {settings.MAX_PAGES} (found {len(pages)} pages)")

        return cls.clean_headers_and_footers(pages)

    @classmethod
    def parse_file(cls, file_path: str, filename: str) -> List[ParsedPage]:
        lower_name = filename.lower()
        if lower_name.endswith(".pdf"):
            return cls.parse_pdf(file_path)
        elif lower_name.endswith(".docx"):
            return cls.parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format for {filename}. Only PDF and DOCX are allowed.")
