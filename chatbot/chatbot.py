import spacy
import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from flask import Flask, request, jsonify
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Carregar o modelo do spaCy
nlp = spacy.load('en_core_web_sm')

# Função de pré-processamento
def preprocessing(sentence):
    if isinstance(sentence, str):  # Verificar se é uma string não nula
        # Remover nomes de usuários
        sentence = re.sub(r'@[A-Za-z0-9]+', ' ', sentence)
        # Remover sites
        sentence = re.sub(r'https?://[A-Za-z0-9./]+', ' ', sentence)

        sentence = sentence.replace('.', '')
        sentence = sentence.lower()
        
        # Remover stop words antes da lematização
        tokens = [token.lemma_ for token in nlp(sentence) if not token.is_stop]
        
        tokens = ' '.join([element for element in tokens])
        return tokens
    else:
        return ''  # Retorna uma string vazia se não for uma string não nula

# Carregar os dados
train_data = pd.read_csv(r'Reddit_Data.csv', header=None, names=['clean_comment', 'category'], encoding='latin1')

# Remover linhas com valores nulos
train_data = train_data.dropna(subset=['clean_comment'])

# Separar a base em x e y
x = train_data['clean_comment'].values
y = train_data['category'].values

# Reduzir a quantidade de linhas na base (para processar mais rápido)
x, _, y, _ = train_test_split(x, y, test_size=0.80)

# Subdividir a base em treinamento e teste
x_treino, x_teste, y_treino, y_teste = train_test_split(x, y, test_size=0.2)

print("Preprocessing...")
# Pode demorar cerca de 5 min
x_train_cleaned = [preprocessing(comment) for comment in x_treino]
x_test_cleaned = [preprocessing(comment) for comment in x_teste]

print("Número de documentos vazios após pré-processamento:", sum(len(doc.split()) == 0 for doc in x_train_cleaned))

# Passo 1 - Transformar x em tf-idf
vectorizer = TfidfVectorizer()
x_train_tfidf = vectorizer.fit_transform(x_train_cleaned)

# Passo 2 - Otimizar os vetores
def preprocessing_lemma(sentence):
    tokens = [token.lemma_ for token in nlp(sentence)]
    tokens = ' '.join(element for element in tokens)
    return tokens

x_train_cleaned_lemma = [preprocessing_lemma(comment) for comment in x_train_cleaned]
x_train_tfidf = vectorizer.fit_transform(x_train_cleaned_lemma)

x_test_cleaned_lemma = [preprocessing_lemma(comment) for comment in x_test_cleaned]
x_test_tfidf = vectorizer.transform(x_test_cleaned_lemma)

# Passo 3 - Montar a árvore
model = DecisionTreeClassifier(criterion='entropy')
model.fit(x_train_tfidf, y_treino)

# Passo 4 - Avaliar a qualidade da árvore
predictions = model.predict(x_test_tfidf)
accuracy = accuracy_score(y_teste, predictions)
conf_matrix = confusion_matrix(y_teste, predictions)

print("Accuracy:", accuracy)
print("Confusion Matrix:\n", conf_matrix)

#Função para avaliar uma nova sentença
@app.route('/avaliar_sentimento', methods=['POST'])
def avaliar_sentimento():
    data = request.json
    sentence = data['sentence']

    sentence_cleaned = preprocessing_lemma(preprocessing(sentence))
    sentence_tfidf = vectorizer.transform([sentence_cleaned])
    prediction = model.predict(sentence_tfidf)

    prediction_as_str = str(prediction[0])

    if prediction_as_str == '0':
        resultado = 'frase neutra'
    elif prediction_as_str == '1':
        resultado = 'frase positiva'
    elif prediction_as_str == '-1':
        resultado = 'frase negativa'

    return jsonify({'sentimento': resultado})

if __name__ == '__main__':
    app.run(debug=True)