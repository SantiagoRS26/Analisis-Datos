from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import pathlib, base64, logging, os, time

import pandas as pd
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text

from .downloader import fetch_page
from .utils      import split_urls, slugify
from .analyzer   import (
    split_text_into_chunks, _build_prompt,
    _call_gpt, _strip_fences, _csv_rows
)
from src.graph.analyze_text_data_return_files import analyze_df_return_files

app = FastAPI()
logging.basicConfig(level=logging.INFO)

class OneShotParams(BaseModel):
    url: str
    university: str = "N/A"
    program: str    = "N/A"
    force: bool     = False

@app.post("/analyze_url")
def analyze_url(params: OneShotParams):
    # 1 · Descarga
    info = fetch_page(
        params.url,
        university=params.university,
        program=params.program,
        force=params.force,
    )
    if info.get("error"):
        raise HTTPException(502, f"Download failed: {info['error']}")

    path = pathlib.Path(info["path"])
    kind = info.get("kind", "html").lower()

    # 2 · Extracción de texto plano
    raw_text = (
        extract_text(str(path))
        if kind == "pdf"
        else BeautifulSoup(path.read_text("utf-8", errors="ignore"), "lxml").get_text("\n")
    )

    # 3 · Troceo + GPT → filas CSV
    rows: List[dict] = []
    for chunk in split_text_into_chunks(raw_text, max_chars=10_000):
        prompt = _build_prompt(params.university, params.program, chunk)
        rsp    = _call_gpt(prompt)
        rows  += _csv_rows(_strip_fences(rsp))

    if not rows:
        raise HTTPException(422, "GPT no extrajo datos útiles")

    df = pd.DataFrame(rows)
    if df.empty or "name" not in df.columns:
        raise HTTPException(422, "CSV sin columna ‘name’")

    # 4 · Gráficas → Buffers PNG
    buf_bar, buf_cloud = analyze_df_return_files(df, text_column="name")

    # 5 · Codificamos en base64 para devolver en JSON
    bar_b64   = base64.b64encode(buf_bar.getvalue()).decode()
    cloud_b64 = base64.b64encode(buf_cloud.getvalue()).decode()
    return JSONResponse({
        "status":   "ok",
        "bar_png":  bar_b64,
        "cloud_png": cloud_b64,
        "rows":     len(df)
    })
