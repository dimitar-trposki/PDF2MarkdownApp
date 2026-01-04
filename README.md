# PDF to Markdown Converter

A Django-based web application that converts PDF files into clean, editable Markdown text.  
The app extracts text and images from PDFs, saves images to disk, replaces them with clear placeholders in the text, and provides a live preview editor before download.

---

## ✨ Features

- Upload PDF files through a web interface
- Convert PDF content to Markdown
- Extract images and save them to a project-relative folder
- Replace images in text with readable placeholders (e.g. `[IMAGE: image_1.png]`)
- Live Markdown preview while editing
- Download the final edited text file
- No OS-specific paths (fully portable)
- Safe handling of PDFs with or without images

---

## 🛠️ Tech Stack

- **Backend:** Django (Python)
- **PDF Processing:** `marker-pdf`
- **Markdown Rendering:** `markdown`
- **Frontend:** HTML, CSS, JavaScript (Fetch API)
- **Image Handling:** Pillow (via marker-pdf)

---

## 🚀 How It Works

1. User uploads a PDF file
2. The backend converts the PDF to Markdown
3. Images (if present) are extracted and saved to `exported_images/`
4. Image positions in the text are replaced with placeholders
5. The user can edit the Markdown with a live preview
6. The final text can be downloaded as a `.txt` file

If a PDF contains no images, no image folder is created.

---

## ⚠️ Notes

- Image extraction errors are silently ignored to ensure stability
- The application works on Windows, macOS, and Linux
- Large PDFs may take longer to process on first run due to model loading

---

## 👥 Creators

- **Matej Mitev - 221039**
- **Dimitar Trposki - 221033**
