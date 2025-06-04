from __future__ import annotations
import os
import json
import pathlib
import logging
import time
import openai
from bs4 import BeautifulSoup
from .utils import slugify
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ─────────────────────────── Configuración ────────────────────────────
LOG      = logging.getLogger("analyzer")
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

MODEL    = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-0125")  # o "gpt-4o-mini"
LOG_JSON = pathlib.Path("data/output/download_log.json")
OUT_CSV  = pathlib.Path("data/output/courses_clean.csv")

RAW_GPT = pathlib.Path("data/output/gpt_raw")
RAW_GPT.mkdir(parents=True, exist_ok=True)

# ─────────── Funciones de extracción de texto ─────────────────────────
def _pdf_to_text(path: pathlib.Path) -> str:
    from pdfminer.high_level import extract_text
    return extract_text(str(path))

def _html_to_text(path: pathlib.Path) -> str:
    soup = BeautifulSoup(path.read_text("utf-8", errors="ignore"), "lxml")
    return soup.get_text(separator="\n")

# ─────────── Trocear texto para no exceder contexto ────────────────────
def split_text_into_chunks(text: str, max_chars: int = 10_000) -> list[str]:
    """
    Divide `text` en trozos de hasta `max_chars` caracteres, preferiblemente
    cortando en saltos de línea para que no se rompa a mitad de párrafo.
    """
    lines = text.splitlines(keepends=True)
    chunks: list[str] = []
    current = ""
    for ln in lines:
        # Si al añadir esta línea excedo max_chars, cierro el chunk actual
        if len(current) + len(ln) > max_chars:
            if current:
                chunks.append(current)
            current = ln
        else:
            current += ln

        # En caso de una línea muy larga (más que max_chars), forzamos corte
        if len(current) > max_chars:
            chunks.append(current[:max_chars])
            current = current[max_chars:]

    if current:
        chunks.append(current)
    return chunks

# ─────────── Construcción del prompt en inglés ───────────────────────
def _build_prompt(univ: str, prog: str, content: str) -> list[dict]:
    system = (
        "You are an expert in university curricula. "
        "Return ONLY raw CSV (no markdown, no backticks) "
        "with headers exactly: name,credits,mode. "
        "If credits are missing, leave blank; same for mode."
    )

    user = (
        f"University: {univ}\n"
        f"Program: {prog}\n"
        "Source text between <<< >>>:\n<<<\n"
        f"{content}\n"
        ">>>\n"
        "==> Return the clean CSV now:"
    )
    return [
        {"role": "system",  "content": system},
        {"role": "user",    "content": user}
    ]

def _norm_credits(c):
    try:
        return int(float(c))
    except ValueError:
        return ""

# ─────────── Llamada a OpenAI (idéntica) ──────────────────────────────
def _call_gpt(messages: list[dict]) -> str:
    for i in range(3):
        try:
            rsp = openai.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.0,
            )
            return rsp.choices[0].message.content
        except Exception as e:
            LOG.warning("GPT error (%s), intento %d/3", e, i + 1)
            time.sleep(2 ** i)
    raise RuntimeError("GPT failed 3 times")

def _strip_fences(text: str) -> str:
    """Quita líneas que empiezan por ``` para que el CSV sea puro."""
    return "\n".join(
        ln for ln in text.splitlines()
        if not ln.strip().startswith("```")
    )
    

def _save_raw_gpt(univ, prog, idx, prompt, answer):
    base = f"{slugify(univ)}_{slugify(prog)}_{idx:03}"
    (RAW_GPT / f"{base}_prompt.txt").write_text(prompt,  encoding="utf-8")
    (RAW_GPT / f"{base}_answer.txt").write_text(answer, encoding="utf-8")

    
# ─────────── Parseo del bloque CSV devuelto por el LLM ───────────────
def _csv_rows(text: str) -> list[dict]:
    """
    Dado un bloque de texto con formato CSV (primera línea headers,
    siguientes líneas valores), devuelve una lista de diccionarios:
    [{header1: valor1, header2: valor2, ...}, ...].
    """
    rows: list[dict] = []
    it = (ln.strip() for ln in text.strip().splitlines() if ln.strip())
    try:
        headers = [h.strip().lower() for h in next(it).split(",")]
    except StopIteration:
        return rows
    for ln in it:
        vals = [v.strip() for v in ln.split(",")]
        # Solo añadimos si coincide el número de columnas
        if len(vals) == len(headers):
            rows.append(dict(zip(headers, vals)))
    return rows

# ─────────── Función principal ───────────────────────────────────────
def analyze():
    if not LOG_JSON.exists():
        raise SystemExit("First run: main.py download")

    meta = json.loads(LOG_JSON.read_text(encoding="utf-8"))

    # Si el CSV ya existe, hacemos un backup con timestamp para no sobreescribirlo
    if OUT_CSV.exists():
        bk_name = OUT_CSV.with_name(f"courses_clean_backup_{int(time.time())}.csv")
        OUT_CSV.replace(bk_name)
        LOG.info("Se renombró el CSV previo a: %s", bk_name)

    # Abrimos el CSV en modo escritura y colocamos cabecera
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f_out:
        f_out.write("university,program,name,credits,mode\n")

    # Recorremos cada archivo (sin agrupar) y procesamos de forma incremental
    for entry in meta:
        if entry.get("error"):
            LOG.warning("Omitiendo (error): %s | %s", entry.get("university"), entry.get("program"))
            continue

        univ = entry["university"]
        prog = entry["program"]
        path = pathlib.Path(entry["path"])
        kind = entry.get("kind", "html").lower()

        LOG.info("Procesando archivo: %s | %s → %s", univ, prog, path)
        try:
            raw_text = _pdf_to_text(path) if kind == "pdf" else _html_to_text(path)
        except Exception as e:
            LOG.error("No se pudo leer %s: %s", path, e)
            continue

        # 1. Dividimos el texto en chunks que no excedan max_chars
        chunks = split_text_into_chunks(raw_text, max_chars=10_000)
        all_rows_for_file: list[dict] = []

        # 2. Para cada chunk, llamamos a GPT y acumulamos las filas
        for idx, chunk in enumerate(chunks):
            LOG.info(" → Enviando chunk %d/%d (caracteres=%d)", idx + 1, len(chunks), len(chunk))
            prompt = _build_prompt(univ, prog, chunk)

            try:
                rsp = _call_gpt(prompt)
            except Exception as e:
                LOG.error("GPT falló para %s | %s (chunk %d): %s", univ, prog, idx + 1, e)
                # Si un chunk falla, pasamos al siguiente chunk (no abortamos todo el archivo)
                continue
            
            _save_raw_gpt(univ, prog, idx + 1, prompt[1]["content"], rsp)
            
            # 3. Parseamos el CSV devuelto por GPT
            csv_text = _strip_fences(rsp)
            rows     = _csv_rows(csv_text)
            if not rows:
                LOG.warning("GPT devolvió 0 filas. Primeros 200 chars del chunk ↓\n%s", chunk[:200])
                LOG.warning("Respuesta GPT ↓\n%s", csv_text[:200])
            else:
                all_rows_for_file.extend(rows)

            # Pausita corta para no saturar la API
            time.sleep(0.5)

        # 4. Una vez procesados todos los chunks, escribimos las filas al CSV
        if all_rows_for_file:
            with OUT_CSV.open("a", newline="", encoding="utf-8") as f_out:
                for r in all_rows_for_file:
                    # Cada r debe tener 'name','credits','mode'
                    name    = r.get("name", "").replace(",", " ")
                    credits = _norm_credits(r.get("credits",""))
                    mode    = r.get("mode", "")
                    line = f"{univ.replace(',', ' ')}," \
                           f"{prog.replace(',', ' ')}," \
                           f"{name},{credits},{mode}\n"
                    f_out.write(line)
            LOG.info(" → Guardadas %d filas de %s | %s", len(all_rows_for_file), univ, prog)
        else:
            LOG.warning("No se extrajo ninguna fila para %s | %s", univ, prog)

    LOG.info("Proceso finalizado. CSV disponible en: %s", OUT_CSV)

if __name__ == "__main__":
    analyze()