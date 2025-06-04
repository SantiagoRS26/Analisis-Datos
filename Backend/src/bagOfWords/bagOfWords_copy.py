import pandas as pd
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud

df = pd.read_csv('/content/courses.csv')
df.head()
import nltk
nltk.download('punkt', force=True)
nltk.download('stopwords', force=True)
nltk.download('punkt_tab')
# 2. Importar librerías

# 3. Cargar el CSV
df = pd.read_csv('/content/courses.csv')

# 4. Cambiar aquí el nombre de la columna que quieras procesar
text_column = 'name'

# 5. Función de preprocesamiento con stopwords personalizadas
def preprocess_text(text):
    if not isinstance(text, str):
        return ''
    text = text.lower()  # a minúsculas
    text = re.sub(r'[^a-záéíóúñü\s]', '', text)  # solo letras y espacios

    # Tokenizar
    tokens = word_tokenize(text)

    # Stopwords en inglés + personalizadas
    stop_words = set(stopwords.words('english'))
    custom_stopwords = {'en', 'le', 'cs'}
    stop_words.update(custom_stopwords)

    # Filtrar tokens
    tokens = [word for word in tokens if word not in stop_words]

    return ' '.join(tokens)


# 6. Aplicar el preprocesamiento
df['processed_text'] = df[text_column].apply(preprocess_text)

#6.1 Realizar imputación con mediana
median_credits = df['credits'].median()
df['credits'] = df['credits'].fillna(median_credits)


# 7. Ver resultados
df[['name', 'processed_text']].head()
# 8. Importar librerías adicionales
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# 9. Bolsa de Palabras (Bag of Words)
# Inicializar CountVectorizer
vectorizer = CountVectorizer(max_features=1000) # las 1000 palabras más frecuentes

# Crear la matriz de Bag of Words
X = vectorizer.fit_transform(df['processed_text'])

# Ver las dimensiones de la matriz (número de documentos x número de palabras)
print("Dimensiones de la matriz BoW:", X.shape)

# Ver el vocabulario (las palabras incluidas)
print("\nVocabulario (primeras 10 palabras):", vectorizer.get_feature_names_out()[:10])

# Puedes ver la matriz dispersa X o convertirla a densa si es pequeña (no recomendado para grandes datasets)
# print("\nMatriz BoW (primeras 5 filas, 10 columnas):\n", X[:5, :10].todense())


# 10. Identificación de Temas (Topic Modeling - LDA con scikit-learn)
# Definir el número de temas que quieres identificar
n_components = 5 # Puedes cambiar este número

# Inicializar el modelo LDA
lda = LatentDirichletAllocation(n_components=n_components, random_state=0)

# Ajustar el modelo a la matriz BoW
lda.fit(X)

# 11. Ver los temas encontrados
print(f"\nTemas encontrados (Top 10 palabras por tema):")
feature_names = vectorizer.get_feature_names_out()
for topic_idx, topic in enumerate(lda.components_):
    print(f"Tema #{topic_idx}:")
    print([feature_names[i] for i in topic.argsort()[:-11:-1]]) # Obtener las 10 palabras más importantes
    print("-" * 20)

# 12. Opcional: Asignar el tema dominante a cada documento
# topic_distribution = lda.transform(X)
# df['dominant_topic'] = topic_distribution.argmax(axis=1)
# print("\nDataFrame con el tema dominante asignado:\n", df[['name', 'dominant_topic']].head())
import matplotlib.pyplot as plt
import numpy as np

# Obtener vocabulario y frecuencias
feature_names = vectorizer.get_feature_names_out()
word_freq = np.array(X.sum(axis=0)).flatten()  # suma por columna
word_freq_dict = dict(zip(feature_names, word_freq))

# Ordenar por frecuencia
sorted_items = sorted(word_freq_dict.items(), key=lambda item: item[1], reverse=True)
top_words = sorted_items[:20]  # top 20 palabras

# Separar palabras y valores
words, freqs = zip(*top_words)

# Graficar
plt.figure(figsize=(12, 6))
plt.bar(words, freqs)
plt.xticks(rotation=45, ha='right')
plt.title("Top 20 palabras más frecuentes")
plt.xlabel("Palabras")
plt.ylabel("Frecuencia")
plt.tight_layout()
plt.show()


# Crear texto completo
all_text = ' '.join(df['processed_text'].dropna())

# Crear y mostrar la nube
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)

plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.title("Nube de palabras")
plt.show()
