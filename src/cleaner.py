# src/cleaner.py
"""
Limpieza de HTML conservando la estructura básica.

• Elimina nodos que nunca aportan contenido útil (script, style, nav, …).
• Borra comentarios HTML.
• Deshace envoltorios inútiles (div, span, section, article, …) que solo
  sirvan de contenedor y no aporten semántica, reemplazándolos por su
  contenido interno (unwrap).
• Quita atributos potencialmente ruidosos (class, id, style, onclick, …)
  manteniendo solo los permitidos (p. ej. href en <a>, colspan / rowspan en <td>).

Resultado: un HTML ligero, legible y todavía estructurado.
"""
from __future__ import annotations

import logging
import pathlib
from bs4 import BeautifulSoup, Comment  # type: ignore

# ─────────────────────────────────  CONFIG  ──────────────────────────────
# Etiquetas que se eliminan por completo
STRIP_TAGS = {
    "script", "style", "noscript",
    "header", "footer", "nav", "aside",
    "meta", "link", "svg", "canvas",
}

# Etiquetas que se pueden "desenvolver" (se eliminan dejando contenido)
UNWRAP_TAGS = {
    "div", "span", "section", "article",
}

# Atributos permitidos por etiqueta
WHITELIST_ATTR: dict[str, set[str]] = {
    "a": {"href", "title"},
    "img": {"src", "alt", "title", "width", "height"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan"},
    # tabla sin estilos en línea
}
# Cualquier otro atributo se descarta
# ─────────────────────────────────────────────────────────────────────────


def _clean_attributes(tag) -> None:
    """Quita atributos que no estén en la whitelist para esa etiqueta."""
    allowed = WHITELIST_ATTR.get(tag.name, set())
    for attr in list(tag.attrs):
        if attr not in allowed:
            del tag.attrs[attr]


def clean_html(file_path: pathlib.Path) -> None:
    """Limpia un archivo HTML conservando su estructura."""
    if file_path.suffix.lower() != ".html":
        return  # ignorar PDFs y otros formatos

    logging.info("cleaning %s", file_path)

    raw = file_path.read_text("utf-8", errors="ignore")
    soup = BeautifulSoup(raw, "lxml")

    # 1) Eliminar completamente nodos no deseados
    for tag in soup.find_all(STRIP_TAGS):
        tag.decompose()

    # 2) Eliminar comentarios
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()

    # 3) Desenvolver contenedores genéricos para aplanar DOM
    for tag in soup.find_all(UNWRAP_TAGS):
        tag.unwrap()

    # 4) Limpiar atributos de las etiquetas restantes
    for tag in soup.find_all(True):
        _clean_attributes(tag)

    # 5) Quitar espacios y saltos de línea redundantes
    pretty_html = soup.prettify(formatter="minimal")

    # 6) Añadir DOCTYPE y guardar
    minimal = f"<!DOCTYPE html>\n{pretty_html}"
    file_path.write_text(minimal, "utf-8")
