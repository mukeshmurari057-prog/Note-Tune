"""Create the three binary demo inputs from sample_notes.txt."""

from pathlib import Path

import fitz
from docx import Document
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
TEXT = (ROOT / "sample_notes.txt").read_text(encoding="utf-8")

pdf = fitz.open()
page = pdf.new_page()
page.insert_textbox(fitz.Rect(50, 50, 545, 780), TEXT, fontsize=12)
pdf.save(ROOT / "sample_notes.pdf")
pdf.close()

document = Document()
for paragraph in TEXT.splitlines():
    document.add_paragraph(paragraph)
document.save(ROOT / "sample_notes.docx")

image = Image.new("RGB", (1400, 850), "white")
draw = ImageDraw.Draw(image)
draw.multiline_text((40, 40), TEXT, fill="black", spacing=18)
image.save(ROOT / "sample_notes.png")
