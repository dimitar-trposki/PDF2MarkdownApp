# Plugin-Based PDF to Markdown Django platform 
Each model lives in its own Docker image.

---

# PROJECT ARCHITECTURE

This project uses a layered Docker architecture:

- pdf2md-base  
  Core Django app and shared utilities

- pdf2md-easyocr  
  Base + EasyOCR

- pdf2md-pytesseract  
  Base + PyTesseract

- pdf2md-marker  
  Base + Marker-PDF (deep learning layout + OCR)

- pdf2md-full  
  Base + ALL models

Each model is isolated in its own image to:

- Avoid conflicting versions (for example PyTorch versions)  
- Enable runtime model downloads  
- Install only model specific dependencies  

---

# PLUGIN-STYLE MODEL SYSTEM

Each model:

- Inherits from BasePDFModel  
- Implements predict() function  
- Uses @register_model(key, label)  

---

# ADDING NEW MODEL

---

## STEP 1 — ADD PYTHON MODEL CLASS

Add the class for the model in:

pdf_converter/ocr_models.py

Template:

```python
try:
    import myocr  # replace with your library

    @register_model("myocr", "MyOCR")
    # @register_model(key, Human-readable label shown in UI)

    class MyOCRModel(BasePDFModel):

        def __init__(self, dpi: int = 220):
            self.dpi = dpi  # Dots per image, used by the function pdf_bytes_to_page_images

            # EasyOCR and PyTesseract accept only images, so the pdf needs to be converted into an image
            # If your model directly accepts pdfs you don’t need dpi and pdf_bytes_to_page_images
            # (For such example see the class MarkerModel in ocr_models.py file)

            self.model = myocr.load_model()

        def predict(self, pdf_bytes: bytes) -> str:
            # Change this function to suit your model.
            # The goal of this function is to process the pdf and return text / markdown.
            # Below is an example implementation.

            with tempfile.TemporaryDirectory() as td:
                pages = pdf_bytes_to_page_images(
                    pdf_bytes,
                    Path(td),
                    dpi=self.dpi
                )

                out = []

                for idx, page_path in enumerate(pages, start=1):
                    text = self.model.ocr(str(page_path))
                    text = (text or "").strip()

                    if text:
                        out.append(f"## Page {idx}\n{text}")

                return "\n\n".join(out).strip()

except ImportError:
    pass
```
---

## STEP 2 — CREATE REQUIREMENTS FILE

Create:

requirements/yourmodel.txt

Example:
```
your-ocr-library
torch>=2.5
opencv-python-headless
pillow
numpy
```
Only include Python packages used by your model.

---

## STEP 3 — CREATE DOCKERFILE

Create:

docker/Dockerfile.yourmodel

Template:
``` dockerfile
FROM pdf2md-base AS base

USER root

# Install system libraries required by your model if needed (Optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY requirements/yourmodel.txt /app/requirements/yourmodel.txt

RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements/yourmodel.txt

RUN chown -R appuser:appuser /app
USER appuser
```
---

## STEP 4 — BUILD AND RUN

Only if base changed:
```
docker build -f docker/Dockerfile.base -t pdf2md-base:latest .
```
Build model image:
```
docker build -f docker/Dockerfile.yourmodel -t pdf2md-yourmodel:latest .
```
Run:

For smaller models (EasyOCR, PyTesseract):
```
docker run -p 8000:8000 pdf2md-yourmodel
```
For bigger models (Marker):
```
docker run -p 8000:8000 --memory=10g pdf2md-yourmodel
```
---

# ADDING MODEL TO FULL IMAGE (Optional)

If you want your model to be present in the full image in:

docker/Dockerfile.full

- Add any new system dependencies to the `apt-get install` section
- Add a new `pip install` line for your requirements file:                                                                                                                 
  ```
  && pip install --no-cache-dir -r requirements/yourmodel.txt
  ```     
---

# Download and run already existing docker images
For windows:
 - `docker pull dimitartrposki/pdf2md-base`
 - `docker pull dimitartrposki/pdf2md-easyocr`
 - `docker pull dimitartrposki/pdf2md-pytesseract`
 - `docker pull dimitartrposki/pdf2md-marker`
 - `docker pull dimitartrposki/pdf2md-full`

For Macintosh:
 - `docker pull matejmitev/pdf2md-base`
 - `docker pull matejmitev/pdf2md-easyocr`
 - `docker pull matejmitev/pdf2md-pytesseract`
 - `docker pull matejmitev/pdf2md-marker`
 - `docker pull matejmitev/pdf2md-full`

---

# Creators
- **Dimitar Trposki - 221033**
- **Matej Mitev - 221039**
