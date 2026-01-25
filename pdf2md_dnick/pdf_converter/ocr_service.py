from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List

from django.conf import settings

from .ocr_registry import create_model
from .pdf_to_text_model import _get_images_root_dir

_PLACEHOLDER_RE = re.compile(r"\*\*\[IMAGE:\s*(.+?)\s*]\*\*")


def ocr_export_images(export_id: str, model_key: str) -> Dict[str, str]:
    """
    Returns dict: filename -> extracted_text
    """
    images_root = _get_images_root_dir()
    images_dir = images_root / export_id
    if not images_dir.exists() or not images_dir.is_dir():
        return {}

    model = create_model(model_key)

    out: Dict[str, str] = {}
    for img_path in sorted(images_dir.iterdir()):
        if img_path.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            continue
        try:
            out[img_path.name] = (model.predict(str(img_path)) or "").strip()
        except Exception as e:
            out[img_path.name] = f"[OCR ERROR: {e}]"
    return out


def inject_ocr_into_markdown(markdown_text: str, ocr_map: Dict[str, str]) -> str:
    """
    Replace **[IMAGE: filename]** with an OCR block under it.
    """

    def repl(match: re.Match) -> str:
        filename = match.group(1).strip()
        extracted = ocr_map.get(filename, "").strip()
        if not extracted:
            return f"**[IMAGE: {filename}]**\n\n> [No text detected]\n"
        # format as blockquote to look nice in markdown preview
        lines = "\n".join([f"> {line}" if line.strip() else ">" for line in extracted.splitlines()])
        return f"**[IMAGE: {filename}]**\n\n{lines}\n"

    return _PLACEHOLDER_RE.sub(repl, markdown_text)
