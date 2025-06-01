from __future__ import annotations
import re, logging, pathlib, unicodedata
from typing import TypedDict, Iterable
from bs4 import BeautifulSoup, Tag
import pdfplumber, tabula, pytesseract

class Course(TypedDict, total=False):
    name: str
    code: str
    credits: str
    semester: str
    source_url: str

HEADERS_RE = re.compile(r"""
    \b(
        plan(?:es)?\s+(?:de\s+)?estudios? |
        pensum |
        malla\s+curricular |
        mapa\s+curricular |
        estructura\s+acad(e|é)mica |
        curriculum |
        courses?\s+(list|overview|structure|requirements) |
        modules? |
        programme? |
        insegnamenti
    )\b
""", re.I | re.X)

SEMESTER_RE = re.compile(r"\b(?:sem(?:ester)?|term|period)[\s:-]*(\d+)", re.I)
CODE_RE     = re.compile(r"^[A-Z]{2,}\s?\d{3,4}[A-Z]?$")
CREDITS_RE  = re.compile(r"\b(\d{1,2}\.?\d?)\s*(?:ECTS|credits?|units?)\b", re.I)

# ──────────────────────────────────────────────────────────
# helpers
def normalize_line(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"\s+\(\d+\s*(?:credits?|ects|units?)\)", "", text, flags=re.I)
    return text.strip(" –-")

def looks_like_course_row(txt: str) -> bool:
    return bool(CODE_RE.match(txt) or CREDITS_RE.search(txt))

# ──────────────────────────────────────────────────────────
def extract_courses(file_path: str, url: str) -> list[Course]:
    ext = pathlib.Path(file_path).suffix.lower()
    if ext == ".pdf":
        return _extract_from_pdf(file_path, url)
    html = pathlib.Path(file_path).read_text("utf-8", errors="ignore")
    return _extract_from_html(html, url)

# ──────────────────────────────────────────────────────────
def _extract_from_html(html: str, url: str) -> list[Course]:
    soup = BeautifulSoup(html, "lxml")
    candidates: list[list[Course]] = []

    # 1) encabezados típicos
    for h in soup.find_all(re.compile(r"^h[1-6]$")):
        if not HEADERS_RE.search(h.get_text(" ", strip=True)):
            continue
        for nxt in h.find_all_next(["ul", "ol", "table"], limit=4):
            block = _parse_block(nxt, url)
            if block:
                candidates.append(block)

    # 2) si nada salió, busca tablas con alta densidad académica
    if not candidates:
        for tbl in soup.find_all(["table", "ul", "ol"]):
            blk = _parse_block(tbl, url)
            hits = sum(looks_like_course_row(c["name"]) for c in blk)
            if blk and hits / len(blk) >= 0.4:
                candidates.append(blk)

    if not candidates:
        return _fallback_gpt(html, url)

    # 3) fusiona y deduplica
    merged: list[Course] = []
    seen = set()
    for blk in candidates:
        for c in blk:
            key = (c["name"].lower(), c.get("code") or c["name"][:20])
            if key not in seen:
                seen.add(key)
                merged.append(c)
    return merged

def _parse_block(tag: Tag, url: str) -> list[Course]:
    if tag.name in ("ul", "ol"):
        items = [li.get_text(" ", strip=True) for li in tag.find_all("li", recursive=False)]
    else:
        items = [
            " ".join(td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"]))
            for tr in tag.find_all("tr")
        ]
    out: list[Course] = []
    for raw in items:
        raw = normalize_line(raw)
        if len(raw) < 4:
            continue
        out.append(_parse_course_line(raw, url))
    return out

def _parse_course_line(text: str, url: str) -> Course:
    code = credits = semester = ""
    m = CODE_RE.match(text)
    if m:
        code = m.group(0)
        text = text[len(code):].lstrip(" –-:")

    m = CREDITS_RE.search(text)
    if m:
        credits = m.group(1)
        text = CREDITS_RE.sub("", text, count=1).strip(" –-:")

    m = SEMESTER_RE.search(text)
    if m:
        semester = m.group(1)
        text = SEMESTER_RE.sub("", text, count=1).strip(" –-:")

    name = re.sub(r"\s{2,}", " ", text).strip(" .,–-")
    return Course(name=name, code=code, credits=credits, semester=semester, source_url=url)

# ──────────────────────────────────────────────────────────
def _extract_from_pdf(path: str, url: str) -> list[Course]:
    out: list[Course] = []
    try:
        dfs = tabula.read_pdf(path, pages="all", multiple_tables=True, lattice=True)
        for df in dfs:
            for _, row in df.iterrows():
                joined = " ".join(str(c) for c in row.tolist())
                joined = normalize_line(joined)
                if len(joined) < 4:
                    continue
                out.append(_parse_course_line(joined, url))
        if out:
            return out
    except Exception as exc:
        logging.debug("Tabula fail %s", exc)

    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                for line in page.extract_text().splitlines():
                    line = normalize_line(line)
                    if len(line) < 4 or "course" in line.lower():
                        continue
                    out.append(_parse_course_line(line, url))
        if out:
            return out
    except Exception as exc:
        logging.debug("pdfplumber fail %s", exc)

    # OCR fallback
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                img = page.to_image(resolution=200).original
                text = pytesseract.image_to_string(img)
                for ln in text.splitlines():
                    ln = normalize_line(ln)
                    if len(ln) < 4:
                        continue
                    out.append(_parse_course_line(ln, url))
    except Exception as exc:
        logging.warning("OCR fail %s", exc)

    return out

def _fallback_gpt(html: str, url: str) -> list[Course]:
    logging.info("GPT fallback for %s", url)
    return []
