from __future__ import annotations
from pathlib import Path
import fitz


def pdf_bytes_to_page_images(pdf_bytes: bytes, out_dir: Path, dpi: int = 220) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages: list[Path] = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=dpi)
        p = out_dir / f"page_{i + 1:03d}.png"
        pix.save(str(p))
        pages.append(p)
    return pages
