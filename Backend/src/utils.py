from __future__ import annotations
import re
from typing import Iterable
import re, unicodedata, pathlib

_COMMA_SPLIT = re.compile(r",\s*")

def split_urls(raw: str) -> Iterable[str]:
    """
    Devuelve una lista de URL limpias.
    - Divide por coma.
    - Quita '|' y saltos de línea que a veces usan las universidades.
    - Elimina repetidas preservando orden.
    """
    seen: set[str] = set()
    for part in _COMMA_SPLIT.split(raw.strip()):
        url = part.strip(" |")
        if url and url not in seen:
            seen.add(url)
            yield url

def slugify(text: str, *, maxlen: int | None = 80) -> str:
    """
    Convierte 'Máster en Ciencia  de Datos' ➜ 'master_en_ciencia_de_datos'
    """
    text = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "_", text).strip("_")
    return text[:maxlen] if maxlen else text

def normalize_line(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"\s+\(\d+\s*(?:credits?|ects|units?)\)", "", text, flags=re.I)
    return text.strip(" –-")