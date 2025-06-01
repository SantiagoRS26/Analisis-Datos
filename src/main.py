from .downloader import fetch_page
from .extractor import extract_courses
from .utils import split_urls

import argparse
import json
import pathlib
import pandas as pd

PROG_COL = "Carrera"


def cmd_download(args):
    links = pd.read_csv("data/universidades.csv")
    meta = []

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


def cmd_extract(_args):
    with open("data/output/download_log.json", encoding="utf-8") as fh:
        meta = json.load(fh)

    records = []
    for info in meta:
        if info.get("error"):
            continue
        for c in extract_courses(info["path"], info["url"]):
            records.append(
                {
                    "university": info["university"],
                    "program": info["program"],
                    **c,
                }
            )

    pd.DataFrame(records).to_csv("data/output/courses.csv", index=False)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("download", help="descarga html/pdf")
    d.add_argument("--force", action="store_true", help="ignora cache y re-descarga")

    e = sub.add_parser("extract", help="extrae cursos de archivos ya descargados")

    args = p.parse_args()
    {"download": cmd_download, "extract": cmd_extract}[args.cmd](args)
