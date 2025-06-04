from io import BytesIO

def analyze_text_data_return_files(csv_path: str, text_column: str = 'name'):
    import pandas as pd, re, nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from wordcloud import WordCloud
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    import matplotlib.pyplot as plt
    import numpy as np

    nltk.download('punkt', force=True)
    nltk.download('stopwords', force=True)

    df = pd.read_csv(csv_path)

    def preprocess_text(text):
        if not isinstance(text, str): return ''
        text = text.lower()
        text = re.sub(r'[^a-záéíóúñü\s]', '', text)
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        stop_words.update({'en', 'le', 'cs'})
        return ' '.join([w for w in tokens if w not in stop_words])

    df['processed_text'] = df[text_column].apply(preprocess_text)

    if 'credits' in df.columns:
        df['credits'] = df['credits'].fillna(df['credits'].median())

    vectorizer = CountVectorizer(max_features=1000)
    X = vectorizer.fit_transform(df['processed_text'])

    lda = LatentDirichletAllocation(n_components=5, random_state=0)
    lda.fit(X)

    feature_names = vectorizer.get_feature_names_out()
    word_freq = np.array(X.sum(axis=0)).flatten()
    sorted_items = sorted(zip(feature_names, word_freq), key=lambda x: x[1], reverse=True)
    words, freqs = zip(*sorted_items[:20])

    # --- Gráfico de barras en BytesIO ---
    fig_bar, ax = plt.subplots(figsize=(12, 6))
    ax.bar(words, freqs)
    ax.set_title("Top 20 palabras más frecuentes")
    ax.set_xlabel("Palabras")
    ax.set_ylabel("Frecuencia")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buf_bar = BytesIO()
    fig_bar.savefig(buf_bar, format='png')
    buf_bar.seek(0)
    plt.close(fig_bar)

    # --- Nube de palabras en BytesIO ---
    all_text = ' '.join(df['processed_text'].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)

    fig_cloud, ax2 = plt.subplots(figsize=(12, 6))
    ax2.imshow(wordcloud, interpolation='bilinear')
    ax2.axis("off")
    ax2.set_title("Nube de palabras")

    buf_cloud = BytesIO()
    fig_cloud.savefig(buf_cloud, format='png')
    buf_cloud.seek(0)
    plt.close(fig_cloud)

    return buf_bar, buf_cloud
