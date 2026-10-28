import pytest
from app.services.parser import ParsedPage
from app.services.segmenter import ClauseSegmenter


def test_segmenter_numbering_and_headings():
    raw_text = (
        "1. DEFINITIONS\n"
        "In this Agreement, the following terms shall have the meanings set forth below.\n\n"
        "1.1 'Confidential Information' means any non-public proprietary data disclosed by either party.\n\n"
        "Section 2. TERMINATION\n"
        "Either party may terminate this Agreement upon at least thirty (30) days prior written notice.\n\n"
        "(a) In the event of material breach, termination shall be effective within ten days.\n\n"
        "IN WITNESS WHEREOF, the parties hereto have executed this Agreement."
    )
    pages = [ParsedPage(page_number=1, text=raw_text)]
    clauses = ClauseSegmenter.segment_pages(pages)

    assert len(clauses) >= 3
    headings = [c.heading for c in clauses if c.heading]
    assert any("DEFINITIONS" in h for h in headings)
    assert any("TERMINATION" in h for h in headings)


def test_segmenter_fragment_merging():
    # A short fragment of 6 words followed by another paragraph
    raw_text = (
        "1. SCOPE OF SERVICES\n"
        "Short clause.\n\n"  # 2 words -> should be merged
        "The consultant shall deliver regular bi-weekly status reports and attend required sprint planning meetings with company engineering leads."
    )
    pages = [ParsedPage(page_number=1, text=raw_text)]
    clauses = ClauseSegmenter.segment_pages(pages)

    # Should be merged into 1 clause instead of 2 fragments
    assert len(clauses) == 1
    assert "Short clause." in clauses[0].text
    assert "bi-weekly status reports" in clauses[0].text


def test_segmenter_long_clause_splitting():
    # Create a long paragraph of > 450 words
    sentences = [f"Sentence number {i} provides detailed contractual terms and specifications." for i in range(50)]
    long_text = "Section 5. EXTENDED SPECIFICATION\n" + " ".join(sentences)

    pages = [ParsedPage(page_number=1, text=long_text)]
    clauses = ClauseSegmenter.segment_pages(pages)

    # Must be split into parts
    assert len(clauses) > 1
    assert any("Part" in (c.heading or "") for c in clauses)
