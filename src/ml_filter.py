# ml_filter.py -------------------------------------------------------------
import pathlib
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


def train(tsv_path="data/train_samples.tsv", model_out="data/lineclf.joblib"):
    """Entrena el mini-clasificador y lo guarda en `model_out`."""
    tsv_path = pathlib.Path(tsv_path)
    if not tsv_path.is_file():
        raise FileNotFoundError(f"No existe: {tsv_path}")

    df = pd.read_csv(tsv_path, sep="\t")
    if {"label", "text"} - set(df.columns):
        raise ValueError("El TSV debe tener columnas 'label' y 'text'")

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"],
        test_size=0.2, stratify=df["label"], random_state=42
    )

    vec = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        stop_words=("english"),
        sublinear_tf=True,
        max_features=20_000
    )
    clf = LinearSVC(C=1.0)

    X_tr = vec.fit_transform(X_train)
    clf.fit(X_tr, y_train)

    print("\n=== Métricas de validación ===")
    print(classification_report(y_test, clf.predict(vec.transform(X_test))))

    out_path = pathlib.Path(model_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"vec": vec, "clf": clf}, out_path)
    print(f"✅ Modelo guardado en {out_path.resolve()}\n")


def predict(texts, model_path="data/lineclf.joblib"):
    """Devuelve 1 (=curso) / 0 para cada texto."""
    saved = joblib.load(model_path)
    vec, clf = saved["vec"], saved["clf"]
    return clf.predict(vec.transform(texts))


# ───────────────────────── CLI ──────────────────────────
if __name__ == "__main__":
    import argparse, sys

    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["train", "predict"],
                   help="train → entrena; predict → clasifica una frase")
    p.add_argument("arg", nargs="?", help="TSV (train) o frase (predict)")
    args = p.parse_args()

    if args.cmd == "train":
        train(tsv_path=args.arg or "data/train_samples.tsv")
