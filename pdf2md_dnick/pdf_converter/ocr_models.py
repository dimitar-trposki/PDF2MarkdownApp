from __future__ import annotations
import os, tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from .ocr_registry import register_model, register_factory
from .pdf_pages import pdf_bytes_to_page_images


# ===== Base =====
class BasePDFModel(ABC):
    name: str

    @abstractmethod
    def run_on_pdf(self, pdf_bytes: bytes) -> str:
        """Return extracted text/markdown using ONLY this model."""
        raise NotImplementedError


class ImageOCRPDFModel(BasePDFModel):
    """For models that only OCR images: PDF -> page images -> predict_image() per page."""
    dpi: int = 220

    @abstractmethod
    def predict_image(self, image_path: str) -> str:
        raise NotImplementedError

    def run_on_pdf(self, pdf_bytes: bytes) -> str:
        with tempfile.TemporaryDirectory() as td:
            pages = pdf_bytes_to_page_images(pdf_bytes, Path(td), dpi=self.dpi)
            out = []
            for idx, p in enumerate(pages, start=1):
                t = (self.predict_image(str(p)) or "").strip()
                if t:
                    out.append(f"## Page {idx}\n{t}")
            return "\n\n".join(out).strip()


# ===== EasyOCR =====
@register_model("easyocr_en", "EasyOCR (en)")
class EasyOCRModel(ImageOCRPDFModel):
    def __init__(self, lang: str = "en", gpu: bool = False):
        self.name = f"easyocr[{lang}]"
        import easyocr
        self.reader = easyocr.Reader([lang], gpu=gpu)

    def predict_image(self, image_path: str) -> str:
        results = self.reader.readtext(image_path, detail=0)
        return "\n".join(results).strip()


register_factory("easyocr_mk", "EasyOCR (mk)", lambda: EasyOCRModel(lang="mk", gpu=False))


# ===== PyTesseract =====
@register_model("pytesseract_eng", "PyTesseract (eng)")
class PyTesseractModel(ImageOCRPDFModel):
    def __init__(self, lang: Optional[str] = None):
        self.name = "pytesseract"
        import pytesseract
        from PIL import Image
        self._tess = pytesseract
        self._Image = Image

        tesseract_cmd = os.getenv("TESSERACT_CMD")
        if tesseract_cmd:
            self._tess.pytesseract.tesseract_cmd = tesseract_cmd

        self.lang = lang or os.getenv("TESSERACT_LANG", "eng")

    def predict_image(self, image_path: str) -> str:
        img = self._Image.open(image_path)
        return (self._tess.image_to_string(img, lang=self.lang) or "").strip()


# ===== OpenAI Vision (optional) =====
try:
    from openai import OpenAI
    import base64


    @register_model("openai_vision", "OpenAI Vision OCR")
    class OpenAIVisionOCRModel(ImageOCRPDFModel):
        def __init__(self, model: Optional[str] = None):
            self.name = "openai-vision"
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY is not set")
            self.client = OpenAI(api_key=api_key)
            self.model_name = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

        def _data_url(self, path: str) -> str:
            b = Path(path).read_bytes()
            return "data:image/png;base64," + base64.b64encode(b).decode("utf-8")

        def predict_image(self, image_path: str) -> str:
            resp = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": (
                            "Extract ALL text from this image exactly as it appears. "
                            "The text may be in Macedonian (Cyrillic). "
                            "Do NOT translate or summarize; just transcribe."
                        )},
                        {"type": "image_url", "image_url": {"url": self._data_url(image_path)}},
                    ],
                }],
                temperature=0.0,
            )
            return (resp.choices[0].message.content or "").strip()

except Exception:
    pass

# ===== Gemini Vision (optional) =====
try:
    from google import genai
    from google.genai import types


    @register_model("gemini_vision", "Gemini Vision OCR")
    class GeminiVisionOCRModel(ImageOCRPDFModel):
        def __init__(self, model: Optional[str] = None):
            self.name = "gemini-vision"
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError("GEMINI_API_KEY is not set")
            self.model_name = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            self.client = genai.Client(api_key=api_key)

        def predict_image(self, image_path: str) -> str:
            b = Path(image_path).read_bytes()
            prompt = (
                "Extract ALL text from this image exactly as it appears. "
                "The text may be in Macedonian (Cyrillic). "
                "Do NOT translate or summarize; just transcribe."
            )
            resp = self.client.models.generate_content(
                model=self.model_name,
                contents=[types.Part.from_bytes(data=b, mime_type="image/png"), prompt],
            )
            return (resp.text or "").strip()

except Exception:
    pass

# ===== Marker is separate & does PDF->Markdown directly (optional) =====
try:
    from .pdf_models_marker import marker_pdf_bytes_to_markdown


    @register_model("marker", "Marker (PDF → Markdown)")
    class MarkerModel(BasePDFModel):
        def __init__(self):
            self.name = "marker"

        def run_on_pdf(self, pdf_bytes: bytes) -> str:
            return marker_pdf_bytes_to_markdown(pdf_bytes)

except Exception:
    pass
