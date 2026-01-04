import os
import re
import tempfile
import uuid
from pathlib import Path

from django.conf import settings

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

_converter = PdfConverter(artifact_dict=create_model_dict())


def _get_images_root_dir() -> Path:
    out = getattr(settings, "PDF_IMAGE_OUTPUT_DIR", None)
    if out:
        return Path(out)
    return Path(settings.BASE_DIR) / "exported_images"


def _replace_image_tags_with_placeholders(markdown_text: str, image_names: list[str]) -> str:
    """
    Replace markdown image tags that reference any of the extracted image names with
    a readable placeholder: **[IMAGE: filename.png]**
    """
    text = markdown_text

    for name in image_names:
        try:
            pattern = re.compile(
                r"!\[[^]]*]\([^)<>]*" + re.escape(name) + r"[^)]*\)",
                flags=re.IGNORECASE
            )
            text = pattern.sub(f"**[IMAGE: {name}]**", text)
        except Exception:
            continue

    return text


def pdf_bytes_to_markdown(pdf_bytes: bytes) -> str:
    """
    Converts PDF bytes to Markdown using marker-pdf.
    Images are saved ONLY if at least one image exists.
    Image-related failures are silently ignored.
    """
    tmp_path = None

    export_id = uuid.uuid4().hex[:10]
    images_root = _get_images_root_dir()
    images_dir = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            tmp_path = f.name
            f.write(pdf_bytes)

        rendered = _converter(tmp_path)
        markdown_text, _, images = text_from_rendered(rendered)

        saved_names = []

        if isinstance(images, dict):
            for raw_name, img in images.items():
                try:
                    if img is None:
                        continue

                    if images_dir is None:
                        images_dir = images_root / export_id
                        images_dir.mkdir(parents=True, exist_ok=True)

                    filename = Path(raw_name).name or f"image_{len(saved_names)}.png"

                    if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                        filename += ".png"

                    out_path = images_dir / filename
                    img.save(out_path)

                    saved_names.append(filename)

                except Exception:
                    continue

        markdown_text = _replace_image_tags_with_placeholders(markdown_text, saved_names)

        if images_dir and saved_names:
            markdown_text = (
                    f"> Images exported to: {images_dir}\n\n"
                    + markdown_text
            )

        return markdown_text

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

# Only handles text, not images
# import tempfile
# import os
#
# from marker.converters.pdf import PdfConverter
# from marker.models import create_model_dict
# from marker.output import text_from_rendered
#
# _converter = PdfConverter(artifact_dict=create_model_dict())
#
#
# def pdf_bytes_to_markdown(pdf_bytes: bytes) -> str:
#     tmp_path = None
#
#     try:
#         with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
#             tmp_path = f.name
#             f.write(pdf_bytes)
#
#         rendered = _converter(tmp_path)
#         text, _, _images = text_from_rendered(rendered)
#         return text
#
#     finally:
#         if tmp_path and os.path.exists(tmp_path):
#             os.remove(tmp_path)
