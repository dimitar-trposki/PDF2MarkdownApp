from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("convert/", views.convert_pdf, name="convert_pdf"),
    path("render/", views.render_markdown, name="render_markdown"),
    path("download/", views.download_text, name="download_text"),
]
