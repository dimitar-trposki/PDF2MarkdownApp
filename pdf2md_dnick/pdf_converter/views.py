from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
import re

import markdown as md

from .pdf_to_text_model import pdf_bytes_to_markdown


def home(request):
    get_token(request)
    return render(request, "pdf_converter/home.html")


def normalize_markdown_spacing(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("\u00A0", " ")
    s = re.sub(r"[\u200B-\u200D\uFEFF]", "", s)
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()


@require_http_methods(["POST"])
def convert_pdf(request):
    uploaded = request.FILES.get("pdf")
    if not uploaded:
        return JsonResponse({"error": "No PDF uploaded."}, status=400)

    if not uploaded.name.lower().endswith(".pdf"):
        return JsonResponse({"error": "File must be a PDF."}, status=400)

    pdf_bytes = uploaded.read()

    try:
        markdown_text = pdf_bytes_to_markdown(pdf_bytes)
        markdown_text = normalize_markdown_spacing(markdown_text)
    except Exception as e:
        return JsonResponse({"error": f"Conversion failed: {str(e)}"}, status=500)

    preview_html = md.markdown(
        markdown_text,
        extensions=["fenced_code", "tables", "toc", "nl2br"]
    )

    return JsonResponse({
        "markdown": markdown_text,
        "preview_html": preview_html
    })


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


@require_http_methods(["POST"])
def render_markdown(request):
    text = request.POST.get("text", "")
    text = normalize_markdown_spacing(text)

    preview_html = md.markdown(
        text,
        extensions=["fenced_code", "tables", "toc", "nl2br"]
    )

    return JsonResponse({"preview_html": preview_html})
