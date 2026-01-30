"""
 Models for PDF to Markdown conversion.

All models inherit from BasePDFModel and implement the predict() method.
To add a new model:
    1. Create a class inheriting from BasePDFModel
    2. Implement predict()
    3. Use @register_model("key", "Display Label") decorator
    4. Wrap in try/except if the model has optional dependencies

Models are conditionally registered based on available dependencies,
allowing Docker images to include only specific models.
"""

from __future__ import annotations
import os
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from .ocr_registry import register_model
from .pdf_pages import pdf_bytes_to_page_images


class BasePDFModel(ABC):
    """
    Abstract base class for all PDF to Markdown models.

    Every model must implement the predict() method which takes
    raw PDF bytes and returns extracted text/markdown.
    """

    @abstractmethod
    def predict(self, pdf_bytes: bytes) -> str:
        """
        Args:
            pdf_bytes: Raw bytes of the PDF file.

        Returns:
            Extracted text or markdown string.
        """
        raise NotImplementedError


# =============================================================================
# EasyOCR Model
# =============================================================================
try:
    import easyocr as _easyocr_module

    @register_model("easyocr", "EasyOCR")
    class EasyOCRModel(BasePDFModel):
        def __init__(self, lang: str = "ru", gpu: bool = False, dpi: int = 220):
            import easyocr
            self.lang = lang
            self.dpi = dpi
            self.reader = easyocr.Reader([lang], gpu=gpu)

        def predict(self, pdf_bytes: bytes) -> str:
            with tempfile.TemporaryDirectory() as td:
                pages = pdf_bytes_to_page_images(pdf_bytes, Path(td), dpi=self.dpi)
                out = []
                for idx, page_path in enumerate(pages, start=1):
                    results = self.reader.readtext(str(page_path), detail=0)
                    text = "\n".join(results).strip()
                    if text:
                        out.append(f"## Page {idx}\n{text}")
                return "\n\n".join(out).strip()

except ImportError:
    pass


# =============================================================================
# PyTesseract Model
# =============================================================================
try:
    import pytesseract as _pytesseract_module

    @register_model("pytesseract", "PyTesseract")
    class PyTesseractModel(BasePDFModel):

        def __init__(self, lang: Optional[str] = None, dpi: int = 220):
            import pytesseract
            from PIL import Image

            self._tess = pytesseract
            self._Image = Image
            self.dpi = dpi

            tesseract_cmd = os.getenv("TESSERACT_CMD")
            if tesseract_cmd:
                self._tess.pytesseract.tesseract_cmd = tesseract_cmd

            tesseract_lang = os.getenv("TESSERACT_LANG")
            if tesseract_lang:
                self.lang = tesseract_lang
            else:
                self.lang = "mkd"

        def predict(self, pdf_bytes: bytes) -> str:
            with tempfile.TemporaryDirectory() as td:
                pages = pdf_bytes_to_page_images(pdf_bytes, Path(td), dpi=self.dpi)
                out = []
                for idx, page_path in enumerate(pages, start=1):
                    img = self._Image.open(page_path)
                    text = (self._tess.image_to_string(img, lang=self.lang) or "").strip()
                    if text:
                        out.append(f"## Page {idx}\n{text}")
                return "\n\n".join(out).strip()

except ImportError:
    pass


# =============================================================================
# Marker Model
# =============================================================================
try:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered

    _marker_converter = None

    def _get_marker_converter():
        """Lazy initialization of Marker converter."""
        global _marker_converter
        if _marker_converter is None:
            _marker_converter = PdfConverter(artifact_dict=create_model_dict())
        return _marker_converter

    @register_model("marker", "Marker")
    class MarkerModel(BasePDFModel):

        def __init__(self):
            self._converter = None

        def predict(self, pdf_bytes: bytes) -> str:
            if self._converter is None:
                self._converter = _get_marker_converter()

            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                    tmp_path = f.name
                    f.write(pdf_bytes)

                rendered = self._converter(tmp_path)
                text, _, _ = text_from_rendered(rendered)
                return (text or "").strip()

            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass

except ImportError:
    pass
except Exception:
    pass
