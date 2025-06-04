# extractor.py
# ──────────────────────────────────────────────────────────────
# High-recall / high-precision extractor of course lists from
# HTML or PDF files (Spanish / English).
#
# Jun-2025 — incluye:
#   • filtrado heurístico avanzado de filas “no curso”
#   • parsers separados para <table> vs <ul>/<ol>
#   • expresiones regulares ampliadas (créditos ES, códigos con guion, …)
#   • acotación de la búsqueda a la sección curricular
# ──────────────────────────────────────────────────────────────
from __future__ import annotations

import logging
logger = logging.getLogger(__name__)  

import pathlib
import re
import unicodedata
from typing import Iterable, TypedDict

import pdfplumber
import pytesseract
import tabula
from bs4 import BeautifulSoup, Tag


try:
    from src.ml_filter import predict as ml_predict
    _ML_READY = True
    logger.info("🧠 ML filter loaded (predict)")
except Exception as e:
    _ML_READY = False
    logger.warning("⚠️  ML filter NOT loaded: %s", e)

# ──────────────────────────────────────────────────────────────
class Course(TypedDict, total=False):
    name: str
    code: str
    credits: str
    semester: str
    source_url: str


# ───────────────────────── regex “dialect”
HEADERS_RE = re.compile(
    r"""
    \b(
        plan(?:es)?\s+(?:de\s+)?estudios?   |
        pensum                              |
        malla\s+curricular                  |
        mapa\s+curricular                   |
        estructura\s+acad(e|é)mica          |
        curriculum                          |
        courses?\s+(list|overview|structure|requirements) |
        modules?                            |
        programme?                          |
        insegnamenti
    )\b
""",
    re.I | re.X,
)

# códigos tipo CS-101, MAT1234-A, INF 201
CODE_RE = re.compile(r"^[A-Z]{2,}[-\s]?\d{2,4}[A-Z]?$")

# créditos en inglés o español, con coma o punto decimal
CREDITS_RE = re.compile(
    r"\b(\d{1,2}(?:[.,]\d)?)\s*(?:ECTS|cr[eé]ditos?|credits?|units?)\b", re.I
)

SEMESTER_RE = re.compile(
    r"\b(?:sem(?:ester)?|cuatrimestre|trimestre|term|period)[\s:-]*(\d+)", re.I
)

# “palabras tóxicas” típicas de líneas que NO son cursos
BAD_PAT = re.compile(
    r"\b("
    r"tuition|fee[s]?|apply|application|deadline|ielts|toefl|gpa|"
    r"college|school|university|faculty|department|professor|lecturer|dean|"
    r"duration|year[s]?|contact|student[s]?|resident[s]?"
    r")\b",
    re.I,
)

# ──────────────────────────────────────────────────────────────
# helpers
def normalize_line(text: str) -> str:
    """Unicode NFKD + eliminación de ‘(3 credits)’ inline + trims."""
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(
        r"\s+\(\d+\s*(?:credits?|ects|units?)\)", "", text, flags=re.I
    )  # '(3 credits)'
    return text.strip(" –—-").strip()


def looks_like_course_row(txt: str) -> bool:
    """
    Heurística rápida de doble filo: intenta incluir
    títulos de asignaturas y excluir la morralla administrativa.
    """
    txt = txt.strip()

    # muy corto / muy largo → sospechoso
    if not 4 <= len(txt) <= 120:
        return False

    # stop-words “administrativas”
    if BAD_PAT.search(txt):
        return False

    # Si empieza por código formal o contiene créditos explícitos → OK
    if CODE_RE.match(txt.split()[0]) or CREDITS_RE.search(txt):
        return True

    # ≥2 palabras con Mayúscula inicial en las 3 primeras → típico título
    caps = sum(w[:1].isupper() for w in txt.split()[:3])
    return caps >= 2


def _col_index(header_row: Iterable[str], aliases: set[str]) -> int | None:
    """Devuelve el índice de la primera cabecera cuyo texto contenga un alias."""
    for i, htxt in enumerate(header_row):
        for alias in aliases:
            if alias in htxt:
                return i
    return None


# ──────────────────────────────────────────────────────────────
def extract_courses(file_path: str, url: str) -> list[Course]:
    """
    Entry-point público. Decide el backend según extensión.
    """
    ext = pathlib.Path(file_path).suffix.lower()
    if ext == ".pdf":
        return _extract_from_pdf(file_path, url)

    html = pathlib.Path(file_path).read_text("utf-8", errors="ignore")
    return _extract_from_html(html, url)


# ───────────────────────── HTML ───────────────────────────────
def _extract_from_html(html: str, url: str) -> list[Course]:
    soup = BeautifulSoup(html, "lxml")
    candidates: list[list[Course]] = []

    # 1) Explora secciones encabezadas por h1-h6 “curriculares”
    for h in soup.find_all(re.compile(r"^h[1-6]$")):
        if not HEADERS_RE.search(h.get_text(" ", strip=True)):
            continue

        header_level = int(h.name[1])

        for sib in h.next_siblings:
            # fin de la sección si aparece otro encabezado del mismo
            if isinstance(sib, Tag) and re.match(
                r"^h[1-6]$", sib.name
            ) and int(sib.name[1]) <= header_level:
                break

            if isinstance(sib, Tag) and sib.name in {"ul", "ol", "table"}:
                block = _parse_block(sib, url)
                if block:
                    candidates.append(block)

    # 2) fallback: tablas / listas densas en créditos/códigos
    if not candidates:
        for tbl in soup.find_all(["table", "ul", "ol"]):
            blk = _parse_block(tbl, url)
            if blk:
                score = sum(looks_like_course_row(c["name"]) for c in blk) / len(blk)
                if score >= 0.4:
                    candidates.append(blk)

    if not candidates:
        return _fallback_gpt(html, url)

    # 3) unión + deduplicado
    merged: list[Course] = []
    seen = set()
    for blk in candidates:
        for c in blk:
            key = (c["name"].lower(), c.get("code") or c["name"][:15])
            if key not in seen and len(c["name"]) >= 4:
                seen.add(key)
                merged.append(c)
    if _ML_READY and merged:
        print("Si esta funcionando el ML")
        keep_mask = ml_predict([c["name"] for c in merged]) == 1
        merged = [c for c, keep in zip(merged, keep_mask) if keep]
        
    logging.info("merged=%d  (_ML_READY=%s)", len(merged), _ML_READY)
    return merged


def _parse_block(tag: Tag, url: str) -> list[Course]:
    """Deriva a parser de tabla o lista; aplica filtro heurístico."""
    if tag.name == "table":
        return _parse_table(tag, url)
    return _parse_list(tag, url)


def _parse_list(ul: Tag, url: str) -> list[Course]:
    items = [
        li.get_text(" ", strip=True) for li in ul.find_all("li", recursive=False)
    ]
    out: list[Course] = []
    for raw in items:
        raw = normalize_line(raw)
        if not looks_like_course_row(raw):
            continue
        out.append(_parse_course_line(raw, url))
    return out


def _parse_table(tbl: Tag, url: str) -> list[Course]:
    """
    Extrae por columnas cuando existen cabeceras ‘Code / Course / Credits…’.
    Si no hay cabeceras clarísimas, colapsa la fila entera como antes.
    """
    rows = [
        [c.get_text(" ", strip=True) for c in r.find_all(["td", "th"])]
        for r in tbl.find_all("tr")
    ]
    if not rows:
        return []

    header = [h.lower() for h in rows[0]]
    idx_code = _col_index(header, {"code", "código"})
    idx_name = _col_index(header, {"course", "materia", "asignatura", "module"})
    idx_cr = _col_index(header, {"credit", "crédito", "ects", "units"})
    idx_sem = _col_index(header, {"semester", "semestre", "term"})

    out: list[Course] = []

    # si detectamos al menos una columna significativa, parseamos “por campos”
    if any(i is not None for i in (idx_code, idx_name, idx_cr)):
        for r in rows[1:]:
            if not any(r):
                continue
            name_txt = (
                r[idx_name]
                if idx_name is not None and idx_name < len(r)
                else " ".join(r).strip()
            )
            name_txt = normalize_line(name_txt)
            if not looks_like_course_row(name_txt):
                continue
            out.append(
                Course(
                    name=name_txt,
                    code=r[idx_code].strip()
                    if idx_code is not None and idx_code < len(r)
                    else "",
                    credits=r[idx_cr].strip()
                    if idx_cr is not None and idx_cr < len(r)
                    else "",
                    semester=r[idx_sem].strip()
                    if idx_sem is not None and idx_sem < len(r)
                    else "",
                    source_url=url,
                )
            )
    else:
        # de lo contrario, modo “fila entera” para no perder nada
        for r in rows:
            joined = normalize_line(" ".join(r))
            if looks_like_course_row(joined):
                out.append(_parse_course_line(joined, url))

    return out


def _parse_course_line(text: str, url: str) -> Course:
    """
    Fallback splitter que intenta extraer código, créditos, semestre in-line.
    """
    code = credits = semester = ""
    # — código
    if CODE_RE.match(text):
        code = CODE_RE.match(text).group(0)
        text = text[len(code) :].lstrip(" –—-:")

    # — créditos
    m = CREDITS_RE.search(text)
    if m:
        credits = m.group(1).replace(",", ".")
        text = CREDITS_RE.sub("", text, count=1).strip(" –—-:")

    # — semester
    m = SEMESTER_RE.search(text)
    if m:
        semester = m.group(1)
        text = SEMESTER_RE.sub("", text, count=1).strip(" –—-:")

    name = re.sub(r"\s{2,}", " ", text).strip(" .,–—-")
    return Course(name=name, code=code, credits=credits, semester=semester, source_url=url)


# ───────────────────────── PDF ────────────────────────────────
def _extract_from_pdf(path: str, url: str) -> list[Course]:
    out: list[Course] = []

    # 1) Tabula — intenta capturar tablas bien formadas
    try:
        dfs = tabula.read_pdf(path, pages="all", multiple_tables=True, lattice=True)
        for df in dfs:
            for _, row in df.iterrows():
                joined = normalize_line(" ".join(str(c) for c in row.tolist()))
                if looks_like_course_row(joined):
                    out.append(_parse_course_line(joined, url))
        if out:
            return out
    except Exception as exc:
        logging.debug("Tabula fail %s", exc)

    # 2) pdfplumber — text layer
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                for line in page.extract_text().splitlines():
                    line = normalize_line(line)
                    if looks_like_course_row(line):
                        out.append(_parse_course_line(line, url))
        if out:
            return out
    except Exception as exc:
        logging.debug("pdfplumber fail %s", exc)

    # 3) OCR fallback (pytesseract)
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                img = page.to_image(resolution=200).original
                text = pytesseract.image_to_string(img)
                for ln in text.splitlines():
                    ln = normalize_line(ln)
                    if looks_like_course_row(ln):
                        out.append(_parse_course_line(ln, url))
    except Exception as exc:
        logging.warning("OCR fail %s", exc)

    return out


# ───────────────────────── GPT fallback (rare) ────────────────
def _fallback_gpt(html: str, url: str) -> list[Course]:
    """
    Placeholder por si se decide usar GPT-API como último recurso.
    Hoy devuelve [], pero queda el hook para logging/telemetría.
    """
    logging.info("GPT fallback for %s", url)
    return []
