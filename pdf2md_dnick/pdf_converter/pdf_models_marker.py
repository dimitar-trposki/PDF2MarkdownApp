from __future__ import annotations
import os, tempfile
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

_converter = PdfConverter(artifact_dict=create_model_dict())


def marker_pdf_bytes_to_markdown(pdf_bytes: bytes) -> str:
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            tmp_path = f.name
            f.write(pdf_bytes)

        rendered = _converter(tmp_path)
        text, _, _images = text_from_rendered(rendered)
        return (text or "").strip()

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
