from __future__ import annotations

import pathlib
import random
import time
import logging
import mimetypes
import tempfile
from typing import TypedDict, Literal

import requests
from requests.adapters import HTTPAdapter, Retry

from .utils import slugify                # ⇦ nuevo
from .cleaner import clean_html           # ⇦ nuevo

RAW_DIR = pathlib.Path("data/raw")
RAW_DIR_HTML = RAW_DIR / "html"
RAW_DIR_PDF = RAW_DIR / "pdf"
for p in (RAW_DIR_HTML, RAW_DIR_PDF):
    p.mkdir(parents=True, exist_ok=True)

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1)"
    " AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]


class DownloadInfo(TypedDict, total=False):
    university: str
    program: str
    url: str
    status: int
    elapsed: float
    path: str
    kind: Literal["html", "pdf"] | str
    error: str


def _build_session(retries: int = 4, backoff: float = 1.5) -> requests.Session:
    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        backoff_factor=backoff,
        respect_retry_after_header=True,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "HEAD"),
        raise_on_status=False,
    )
    s = requests.Session()
    s.headers["User-Agent"] = random.choice(USER_AGENTS)
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s


def fetch_page(
    url: str,
    university: str,
    program: str,                       # ⇦ NUEVO parámetro
    *,
    timeout: tuple[int, int] = (10, 20),
    force: bool = False,
) -> DownloadInfo:
    """
    Descarga un recurso remoto (HTML o PDF), lo guarda en disco y devuelve
    metadatos de la operación.

    - Utiliza caché si el fichero ya existe (salvo force=True).
    - Los HTML se limpian automáticamente al terminar la descarga.
    - El nombre del archivo es: <universidad>_<programa>.<ext>
    """

    info: DownloadInfo = {
        "university": university,
        "program": program,
        "url": url,
    }
    t0 = time.perf_counter()

    # ──────────────── Construcción del nombre de salida ────────────────
    slug_univ = slugify(university)
    slug_prog = slugify(program)
    basename = f"{slug_univ}_{slug_prog}"

    guessed_ext = pathlib.Path(url).suffix.lower() or ".html"
    out_path = (
        (RAW_DIR_PDF if guessed_ext == ".pdf" else RAW_DIR_HTML)
        / f"{basename}{guessed_ext}"
    )
    # ───────────────────────────── Caché ───────────────────────────────
    if out_path.exists() and out_path.stat().st_size > 0 and not force:
        info.update(
            status=200,
            elapsed=0.0,
            path=str(out_path),
            kind="pdf" if out_path.suffix == ".pdf" else "html",
        )
        return info
    # ────────────────────────────────────────────────────────────────────

    try:
        with _build_session().get(url, timeout=timeout, stream=True) as r:
            info["status"] = r.status_code
            r.raise_for_status()

            # Detectar tipo real por cabecera
            ctype = r.headers.get("Content-Type", "")
            ext = mimetypes.guess_extension(ctype.partition(";")[0].strip()) or guessed_ext
            kind = "pdf" if "pdf" in (ctype or "").lower() or ext == ".pdf" else "html"
            info["kind"] = kind

            # Ajustar ruta si la extensión cambió
            if ext != out_path.suffix:
                out_path = (
                    RAW_DIR_PDF if kind == "pdf" else RAW_DIR_HTML
                ) / f"{basename}{ext}"

            # Descargar a disco
            with open(out_path, "wb") as fh:
                for chunk in r.iter_content(chunk_size=8192):
                    fh.write(chunk)
            info["path"] = str(out_path)

            # Limpieza si es HTML
            if kind == "html":
                clean_html(out_path)

    except requests.RequestException as exc:
        info["error"] = str(exc)
    finally:
        info["elapsed"] = time.perf_counter() - t0
        logging.info(
            "download %s | %.2fs | %s",
            url,
            info.get("elapsed", 0.0),
            info.get("status"),
        )
        return info
