"""Render every final PDF page and check text bounds; visual review is still required."""
from pathlib import Path
import json
import pymupdf as fitz
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "artifacts" / "report_review"
out.mkdir(parents=True, exist_ok=True)
doc = fitz.open(ROOT / "report" / "main.pdf")
entries = []
thumbs = []
for number, page in enumerate(doc, 1):
    path = out / f"page-{number:02}.png"
    page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4), alpha=False).save(path)
    outside = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                x0, y0, x1, y1 = span["bbox"]
                if x0 < -0.1 or y0 < -0.1 or x1 > page.rect.width + 0.1 or y1 > page.rect.height + 0.1:
                    outside.append(span["text"])
    entries.append({"page": number, "width_pt": page.rect.width, "height_pt": page.rect.height,
                    "text_chars": len(page.get_text()), "outside_page": outside, "raster": path.name})
    im = Image.open(path).convert("RGB")
    im.thumbnail((300, 425))
    tile = Image.new("RGB", (320, 455), "#ededed")
    tile.paste(im, ((320-im.width)//2, 10))
    ImageDraw.Draw(tile).text((12, 436), f"Page {number}", fill="black")
    thumbs.append(tile)
for start in range(0, len(thumbs), 9):
    batch = thumbs[start:start+9]
    sheet = Image.new("RGB", (960, 455*((len(batch)+2)//3)), "#ddd")
    for i, tile in enumerate(batch): sheet.paste(tile, ((i%3)*320, (i//3)*455))
    sheet.save(out/f"contact-{start//9+1}.png")
(out/"page_checks.json").write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"pages":len(doc),"outside_page_spans":sum(len(p["outside_page"]) for p in entries)},ensure_ascii=False))
