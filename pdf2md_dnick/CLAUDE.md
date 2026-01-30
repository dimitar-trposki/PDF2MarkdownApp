# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django web application for converting PDF files to Markdown using multiple OCR and vision models (OpenAI, Gemini, EasyOCR, PyTesseract, Marker).

## Commands

```bash
# Run development server
python manage.py runserver

# Run migrations
python manage.py migrate

# Install dependencies
pip install -r requierements.txt
```

Note: The requirements file has a typo in the filename (`requierements.txt`).

## Architecture

### Model Registry Pattern

The application uses a registry pattern (`pdf_converter/ocr_registry.py`) for pluggable OCR models:
- `@register_model(key, label)` decorator registers model classes
- `register_factory(key, label, factory)` registers factory functions
- `create_model(key)` instantiates models by key and returns `BasePDFModel`
- `safe_list_models()` returns only models that can be instantiated (filters out those missing API keys)

### Model Hierarchy

All models inherit from a single abstract base class:

```
BasePDFModel (abstract)
├── EasyOCRModel (easyocr_en, easyocr_mk)
├── PyTesseractModel (pytesseract_eng)
├── OpenAIVisionOCRModel (openai_vision) - requires OPENAI_API_KEY
├── GeminiVisionOCRModel (gemini_vision) - requires GEMINI_API_KEY
└── MarkerModel (marker) - direct PDF→Markdown
```

Each model implements a single method: `predict(pdf_bytes: bytes) -> str`

Models that need image-based OCR handle PDF-to-image conversion internally using `pdf_pages.pdf_bytes_to_page_images()`.

Models are defined in `pdf_converter/ocr_models.py`. Vision models are conditionally registered only if their dependencies import successfully.

### Request Flow

1. PDF uploaded to `/convert/` with `model_key` parameter
2. `views.convert_pdf()` calls `ocr_registry.create_model(model_key)`
3. Model's `predict(pdf_bytes)` returns markdown
4. View normalizes spacing and converts to HTML preview

### API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Home page |
| POST | `/convert/` | PDF to Markdown (params: `pdf`, `model_key`) |
| POST | `/render/` | Markdown to HTML preview |
| POST | `/download/` | Download text file |
| GET | `/ocr-models/` | List available models |

## Environment Variables

- `OPENAI_API_KEY` - Required for OpenAI Vision model
- `GEMINI_API_KEY` - Required for Gemini Vision model
- `TESSERACT_CMD` - Path to Tesseract executable (if not in PATH)
- `TESSERACT_LANG` - Language for Tesseract (default: "eng")
- `OPENAI_MODEL` - OpenAI model name (default: "gpt-4.1-mini")
- `GEMINI_MODEL` - Gemini model name (default: "gemini-2.0-flash")

## Key Files

- `pdf_converter/views.py` - HTTP endpoints and markdown rendering
- `pdf_converter/ocr_models.py` - All OCR/vision model implementations and BasePDFModel
- `pdf_converter/ocr_registry.py` - Model registration system
- `pdf_converter/pdf_pages.py` - PDF to PNG page conversion (PyMuPDF/fitz)
- `pdf_converter/templates/pdf_converter/home.html` - Frontend UI

## Configuration

Upload limits are set to 30MB in `pdf2md_dnick/settings.py`:
```python
DATA_UPLOAD_MAX_MEMORY_SIZE = 30 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 30 * 1024 * 1024
PDF_IMAGE_OUTPUT_DIR = BASE_DIR / "exported_images"
```

## Adding a New OCR Model

1. Create a class inheriting from `BasePDFModel`
2. Use `@register_model("key", "Display Label")` decorator
3. Implement `predict(self, pdf_bytes: bytes) -> str`
4. Handle any internal conversions (e.g., PDF → images) within `predict()`
5. Wrap in try/except if the model has optional dependencies

Example:

```python
@register_model("my_model", "My Custom Model")
class MyModel(BasePDFModel):
    def __init__(self):
        # Initialize your model/dependencies
        pass

    def predict(self, pdf_bytes: bytes) -> str:
        # Convert PDF bytes to text/markdown
        # Handle PDF→image conversion internally if needed
        return extracted_text
```
