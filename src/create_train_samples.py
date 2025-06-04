# create_train_samples.py
import pandas as pd
from pathlib import Path
import random

# 1) Carga el CSV que generó el extractor
df = pd.read_csv("data/output/courses.csv")  # ajusta la ruta si fuera distinta

# 2) Qué campo contiene la frase a evaluar
candidates = df["name"].dropna().str.strip()

# 3) Elimina duplicados exactos
candidates = candidates.drop_duplicates()

# 4) Selecciona una muestra aleatoria estratificada:
#    – 250 con palabras típicas de curso (alta probabilidad de label=1)
#    – 250 sin esas pistas (mayor incertidumbre → buenos negativos)
with_word = candidates[candidates.str.contains(r"\b(?:credits?|ECTS|Lab|I|II|III)\b", case=False)]
without   = candidates.drop(with_word.index)

n_pos = min(250, len(with_word))
n_neg = min(250, len(without))

sample = pd.concat([
    with_word.sample(n=n_pos, random_state=42),
    without.sample(n=n_neg, random_state=42),
]).sample(frac=1, random_state=42)   # mezclar

# 5) Crea columnas vacías para la etiqueta
train_df = pd.DataFrame({"label": "", "text": sample})
out_path = Path("data/train_samples.tsv")
train_df.to_csv(out_path, sep="\t", index=False)

print(f"✏️  Archivo creado en {out_path} — abrelo en tu editor y rellena la columna 'label' con 1/0") 