from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
import re
import markdown as md

from . import ocr_models
from .ocr_registry import list_models, create_model, safe_list_models


def home(request):
    get_token(request)
    return render(request, "pdf_converter/home.html")


@require_http_methods(["POST"])
def convert_pdf(request):
    uploaded = request.FILES.get("pdf")
    model_key = (request.POST.get("model_key") or "").strip()

    if not uploaded:
        return JsonResponse({"error": "No PDF uploaded."}, status=400)
    if not uploaded.name.lower().endswith(".pdf"):
        return JsonResponse({"error": "File must be a PDF."}, status=400)
    if not model_key:
        return JsonResponse({"error": "Please select a model."}, status=400)

    pdf_bytes = uploaded.read()

    try:
        model = create_model(model_key)
        text = model.predict(pdf_bytes)
        text = normalize_markdown_spacing(text)
    except Exception as e:
        if 'tesseract' in str(e):
            return JsonResponse({"error": "PyTesseract is not installed.\nType this into the terminal:\nbrew install tesseract-lang"}, status=500)
        else:
            return JsonResponse({"error": f"Conversion failed: {str(e)}"}, status=500)

    preview_html = md.markdown(text, extensions=["fenced_code", "tables", "toc", "nl2br"])

    return JsonResponse({"markdown": text, "preview_html": preview_html})


@require_http_methods(["POST"])
def render_markdown(request):
    text = request.POST.get("text", "")
    text = normalize_markdown_spacing(text)

    preview_html = md.markdown(
        text,
        extensions=["fenced_code", "tables", "toc", "nl2br"]
    )
    return JsonResponse({"preview_html": preview_html})


@require_http_methods(["POST"])
def download_text(request):
    text = request.POST.get("text", "")
    filename = request.POST.get("filename", "output.txt")
    if not filename.endswith(".txt"):
        filename += ".txt"

    response = HttpResponse(text, content_type="text/plain; charset=utf-8")
    safe_name = "".join(c for c in filename if c.isalnum() or c in ("-", "_", ".", " "))
    response["Content-Disposition"] = f'attachment; filename="{safe_name}"'
    return response


def ocr_models_api(request):
    models = [{"key": m.key, "label": m.label} for m in safe_list_models()]
    return JsonResponse({"models": models})

def normalize_markdown_spacing(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("\u00A0", " ")
    s = re.sub(r"[\u200B-\u200D\uFEFF]", "", s)
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()