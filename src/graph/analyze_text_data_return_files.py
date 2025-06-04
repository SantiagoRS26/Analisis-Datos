from io import BytesIO

def analyze_df_return_files(df, text_column: str = 'name'):
    import re, nltk, numpy as np, pandas as pd
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from wordcloud import WordCloud
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    import matplotlib.pyplot as plt

    nltk.download('punkt', quiet=True, force=True)
    nltk.download('punkt_tab',  quiet=True, force=True)
    nltk.download('stopwords', quiet=True, force=True)

    def preprocess(t):
        if not isinstance(t, str): return ''
        t = re.sub(r'[^a-záéíóúñü\s]', '', t.lower())
        toks = word_tokenize(t)
        sw   = set(stopwords.words('english')) | {'en', 'le', 'cs'}
        return ' '.join(w for w in toks if w not in sw)

    df['processed_text'] = df[text_column].fillna('').apply(preprocess)

    vect = CountVectorizer(max_features=1000)
    X    = vect.fit_transform(df['processed_text'])

    LDA = LatentDirichletAllocation(n_components=5, random_state=0).fit(X)

    feats, freqs = zip(*sorted(
        zip(vect.get_feature_names_out(), np.array(X.sum(0)).ravel()),
        key=lambda x: x[1], reverse=True
    )[:20])

    # Bar chart
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(feats, freqs)
    ax1.set_title("Top 20 palabras")
    ax1.set_xticklabels(feats, rotation=45, ha='right')
    buf1 = BytesIO(); fig1.savefig(buf1, format='png'); buf1.seek(0); plt.close(fig1)

    # Word cloud
    wc = WordCloud(width=800, height=400, background_color='white')\
            .generate(' '.join(df['processed_text']))
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.imshow(wc, interpolation='bilinear'); ax2.axis('off')
    buf2 = BytesIO(); fig2.savefig(buf2, format='png'); buf2.seek(0); plt.close(fig2)

    return buf1, buf2
