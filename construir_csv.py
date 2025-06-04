#!/usr/bin/env python3
"""
Extrae las hojas 'Hoja 1' y 'Ruben' de Universidades.xlsx y genera
Universidades3.csv agrupando todos los enlaces por Universidad + Carrera.

Uso:
    python construir_csv.py /ruta/Universidades.xlsx [Universidades3.csv]
"""

import sys
import re
import csv
import pandas as pd
import openpyxl


def construir_csv_desde_xlsx(xlsx_path: str, csv_path: str = "Universidades3.csv") -> pd.DataFrame:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    hojas = ["Hoja 1", "Ruben"]

    # {(universidad, carrera): set(enlaces)}
    bolsa: dict[tuple[str, str], set[str]] = {}

    for hoja in hojas:
        ws = wb[hoja]
        universidad = None

        for fila in ws.iter_rows():
            celda_a = fila[0]
            celda_b = fila[1] if len(fila) > 1 else None

            v_a = celda_a.value.strip() if isinstance(celda_a.value, str) else celda_a.value
            v_b = (
                celda_b.value.strip()
                if (celda_b and isinstance(celda_b.value, str))
                else celda_b.value
                if celda_b
                else None
            )

            # --- Caso: fila que define nueva universidad (col A con texto y col B vacía) ---
            if v_a and not v_b:
                universidad = v_a
                continue

            # --- Caso: fila válida de carrera (siempre que haya algo en v_a) ---
            if v_a:
                carrera = re.sub(r"\s+", " ", str(v_a).strip())

                # 1) Si v_b es string y contiene coma interna, tomo todo el texto:
                if isinstance(v_b, str) and "," in v_b:
                    enlace = v_b.strip()

                # 2) Si no, busco hyperlink en A
                elif celda_a.hyperlink:
                    enlace = celda_a.hyperlink.target.strip()

                # 3) Si no, busco hyperlink en B
                elif celda_b and celda_b.hyperlink:
                    enlace = celda_b.hyperlink.target.strip()

                # 4) Si no, y v_b empieza con "http", tomo ese texto
                elif isinstance(v_b, str) and v_b.startswith("http"):
                    enlace = v_b.strip()

                else:
                    enlace = ""

                key = (universidad, carrera)
                bolsa.setdefault(key, set())
                if enlace:
                    # Si venían varias URLs en un solo string, ya las guardo todas tal cual:
                    bolsa[key].add(enlace)

    # --- Convertir el diccionario “bolsa” a lista de filas para DataFrame ---
    filas = []
    for (uni, carrera), enlaces_set in bolsa.items():
        # Cada "enlaces" vendrá como un único string (o varios strings)
        # Por ejemplo: {"https://.../ds/ , https://.../csys/ , ...", "https://otra.com"}.
        # Queremos concatenar todos los elementos del set ordenados, separados por ", "
        # De modo que si hay más de un string (p. ej. varios batches), queden unidos.
        enlaces_ordenados = " , ".join(sorted(enlaces_set))
        filas.append((uni, carrera, enlaces_ordenados))

    df = pd.DataFrame(filas, columns=["Universidad", "Carrera", "Enlace"])

    # --- Exportar a CSV con QUOTE_MINIMAL: sólo se envuelven en comillas los campos que llevan comas ---
    df.to_csv(
        csv_path,
        index=False,
        encoding="utf-8-sig",
        quoting=csv.QUOTE_MINIMAL
    )
    return df


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python construir_csv.py /ruta/Universidades.xlsx [Universidades3.csv]")
        sys.exit(1)

    xlsx_in = sys.argv[1]
    csv_out = sys.argv[2] if len(sys.argv) > 2 else "Universidades3.csv"

    construir_csv_desde_xlsx(xlsx_in, csv_out)
    print(f"CSV generado en: {csv_out}")
