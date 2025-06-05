from __future__ import annotations

import argparse
import json
import logging
import pathlib
import sys

import pandas as pd

from .downloader import fetch_page
from .utils import split_urls

PROG_COL = "Carrera"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
    stream=sys.stdout,
)

# ——————————————————— Sub-comandos ——————————————————————

def cmd_download(args: argparse.Namespace) -> None:
    """
    Lee data/Universidades3.csv, descarga cada enlace (HTML o PDF) y guarda
    data/output/download_log.json con los metadatos de la operación.
    """
    links = pd.read_csv("data/Salida.csv")
    meta: list[dict] = []

    for _, row in links.iterrows():
        university = row["Universidad"]
        program = row[PROG_COL]

        for url in split_urls(row["Enlace"]):
            meta.append(
                fetch_page(
                    url,
                    university=university,
                    program=program,
                    force=args.force,
                )
            )

    pathlib.Path("data/output").mkdir(parents=True, exist_ok=True)
    with open("data/output/download_log.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)


def cmd_analyze(_args: argparse.Namespace) -> None:
    """
    Llama al módulo analyzer.py que usa GPT para leer los archivos descargados
    y generar data/output/courses_clean.csv con:
        university,program,name,credits,modalidad
    """
    # Importación diferida para no cargar openai si solo se hace download
    from . import analyzer
    analyzer.analyze()


# ——————————————————— CLI principal ——————————————————————

if __name__ == "__main__":
    p = argparse.ArgumentParser(prog="univcrawler")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("download", help="descarga html/pdf")
    d.add_argument(
        "--force",
        action="store_true",
        help="ignora caché y re-descarga aunque el archivo exista",
    )

    sub.add_parser("analyze", help="extrae cursos directamente con GPT")

    args = p.parse_args()
    {"download": cmd_download, "analyze": cmd_analyze}[args.cmd](args)
