import re
from typing import List, Optional
from dataclasses import dataclass
from app.services.parser import ParsedPage


@dataclass
class SegmentedClause:
    clause_number: int
    heading: Optional[str]
    text: str
    page_number: int
    start_pos: int
    end_pos: int


class ClauseSegmenter:
    # Heading patterns: Section, Article, Clause, Numbering (1., 1.1, 1.1.1, (a), (i)), ALL CAPS, Title Case
    CLAUSE_START_PATTERN = re.compile(
        r"^(?:"
        r"(?:section|article|clause)\s+\d+(?:\.\d+)*[.:\-–—]?"  # Section 1.2 / Article 3
        r"|\d+(?:\.\d+)+[.:\-–—]?"                             # 1.1 or 1.1.1
        r"|\d+\.[ \t]+"                                        # 1. 
        r"|\([a-z0-9ivxlcdm]+\)[ \t]+"                         # (a) or (1) or (i)
        r"|[A-Z0-9\s]{4,60}:"                                  # ALL CAPS HEADING:
        r")",
        re.IGNORECASE
    )

    SIGNATURE_BLOCK_PATTERN = re.compile(
        r"(IN\s+WITNESS\s+WHEREOF|SIGNATURE\s+PAGE|EXECUTED\s+BY|BY:\s*_{3,}|AUTHORIZED\s+SIGNATURE)",
        re.IGNORECASE
    )

    @classmethod
    def is_heading(cls, line: str) -> bool:
        line = line.strip()
        if not line:
            return False
        if cls.CLAUSE_START_PATTERN.match(line):
            return True
        # Check if line is short ALL CAPS or Title Case heading
        words = line.split()
        if 1 <= len(words) <= 8 and len(line) < 70:
            if line.isupper() and not line.endswith("."):
                return True
            if line.istitle() and not line.endswith("."):
                return True
        return False

    @classmethod
    def split_sentences(cls, text: str) -> List[str]:
        # Split text into sentences at period followed by space and uppercase letter
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
        return [s.strip() for s in sentences if s.strip()]

    @classmethod
    def split_long_clause(cls, text: str, max_words: int = 400) -> List[str]:
        words = text.split()
        if len(words) <= max_words:
            return [text]

        sentences = cls.split_sentences(text)
        chunks: List[str] = []
        current_chunk: List[str] = []
        current_words = 0

        for sentence in sentences:
            s_words = len(sentence.split())
            if current_words + s_words > max_words and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_words = s_words
            else:
                current_chunk.append(sentence)
                current_words += s_words

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks if chunks else [text]

    @classmethod
    def segment_pages(cls, pages: List[ParsedPage]) -> List[SegmentedClause]:
        raw_candidates: List[dict] = []
        running_pos = 0

        current_heading: Optional[str] = None
        current_body: List[str] = []
        current_page_num: int = 1
        clause_start_pos: int = 0

        def flush_clause():
            nonlocal current_heading, current_body, clause_start_pos
            if current_heading or current_body:
                text_content = "\n".join(current_body).strip()
                if not text_content and current_heading:
                    text_content = current_heading
                if text_content:
                    raw_candidates.append({
                        "heading": current_heading,
                        "text": text_content,
                        "page_number": current_page_num,
                        "start_pos": clause_start_pos,
                        "end_pos": clause_start_pos + len(text_content)
                    })
            current_heading = None
            current_body = []

        for page in pages:
            current_page_num = page.page_number
            paragraphs = [p.strip() for p in page.text.split("\n\n") if p.strip()]
            for para in paragraphs:
                lines = [l.strip() for l in para.split("\n") if l.strip()]
                for line in lines:
                    if cls.is_heading(line):
                        flush_clause()
                        current_heading = line
                        clause_start_pos = running_pos
                    else:
                        if current_heading is None and not current_body:
                            clause_start_pos = running_pos
                        current_body.append(line)
                    running_pos += len(line) + 1
                running_pos += 1

        flush_clause()

        if not raw_candidates:
            return []

        # Step 2: Merge fragments shorter than ~25 words with adjacent candidate if unheaded
        merged_candidates: List[dict] = []
        for cand in raw_candidates:
            word_count = len(cand["text"].split())
            if not cand.get("heading") and word_count < 25 and merged_candidates:
                # Merge unheaded fragment into previous clause
                prev = merged_candidates[-1]
                prev["text"] = prev["text"] + "\n" + cand["text"]
                prev["end_pos"] = cand["end_pos"]
            else:
                merged_candidates.append(cand)

        # Step 3: Split clauses longer than ~400 words at sentence boundaries
        final_clauses: List[SegmentedClause] = []
        clause_counter = 1

        for cand in merged_candidates:
            text = cand["text"]
            chunks = cls.split_long_clause(text, max_words=400)
            
            for i, chunk in enumerate(chunks):
                h = cand["heading"]
                if len(chunks) > 1 and h:
                    h = f"{h} (Part {i+1})"
                
                final_clauses.append(SegmentedClause(
                    clause_number=clause_counter,
                    heading=h,
                    text=chunk,
                    page_number=cand["page_number"],
                    start_pos=cand["start_pos"],
                    end_pos=cand["end_pos"]
                ))
                clause_counter += 1

        return final_clauses
