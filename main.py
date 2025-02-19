import os
import json
import requests
from flask import Flask, request, render_template_string, redirect, url_for
from datetime import datetime

# ====== 🔑 CONFIGURATION PERPLEXITY ======
PERPLEXITY_API_KEY = "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"
API_URL = "https://api.perplexity.ai/chat/completions"
HISTORY_FILE = "history.json"

# ====== 🌐 APPLICATION FLASK ======
app = Flask(__name__)

# ====== 🧠 FONCTIONS DE GESTION DE L'HISTORIQUE ======
def save_to_history(sentiment):
    """Ajoute un nouveau résultat dans l'historique et sauvegarde dans history.json."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {"date": timestamp, "sentiment": sentiment}

    # Charge l'historique existant
    history = load_history()
    history.append(new_entry)

    # Sauvegarde l'historique mis à jour
    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

def load_history():
    """Charge l'historique depuis history.json."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as file:
            return json.load(file)
    return []

def delete_entry(index):
    """Supprime un résultat de l'historique en fonction de son index."""
    history = load_history()
    if 0 <= index < len(history):
        del history[index]  # Supprime l'élément
        with open(HISTORY_FILE, "w") as file:
            json.dump(history, file, indent=4)

# ====== 📊 FONCTION POUR RÉCUPÉRER LE SENTIMENT ======
def get_market_sentiment():
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = (
        "Basé sur l’analyse des tendances récentes et des opinions des experts, "
        "quelle est la direction probable du marché américain (S&P500, Nasdaq) pour les 2 à 4 prochaines semaines ? "
        "Réponds UNIQUEMENT par un mot : "
        "- UP (si le marché devrait monter 📈) "
        "- DOWN (si le marché devrait descendre 📉) "
        "- STABLE (si la tendance est neutre ou incertaine ➖) "
        "AUCUNE EXPLICATION. Un seul mot."
    )

    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "Tu es un expert financier."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 20,
        "temperature": 0.0
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            return f"Erreur API ({response.status_code})"

        result = response.json()
        sentiment = result["choices"][0]["message"]["content"].strip()
        
        # Sauvegarde le résultat dans l'historique
        save_to_history(sentiment)
        
        return sentiment
    except Exception as e:
        return f"Erreur : {e}"

# ====== 🌐 PAGE HTML DYNAMIQUE AVEC HISTORIQUE ======
html_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Sentiment du Marché</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background-color: #f0f8ff;
        }
        h1 {
            font-size: 48px;
            color: #2c3e50;
        }
        .sentiment {
            font-size: 100px;
            font-weight: bold;
            color: {% if sentiment == 'UP' %}'#4CAF50'{% elif sentiment == 'DOWN' %}'#E74C3C'{% else %}'#3498DB'{% endif %};
        }
        .timestamp {
            font-size: 20px;
            color: #555;
        }
        form {
            margin-bottom: 30px;
        }
        button {
            font-size: 20px;
            padding: 10px 20px;
            color: white;
            background-color: #2c3e50;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: 0.3s;
        }
        button:hover {
            background-color: #34495e;
        }
        table {
            margin: auto;
            border-collapse: collapse;
            width: 60%;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
        }
        th {
            background-color: #2c3e50;
            color: white;
        }
        .delete-btn {
            color: white;
            background-color: red;
            border: none;
            padding: 5px 10px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>📊 Sentiment du Marché (S&P500 & Nasdaq)</h1>

    <form method="POST" action="/">
        <button type="submit">📊 Mettre à jour le sentiment</button>
    </form>

    {% if sentiment %}
        <div class="sentiment">{{ sentiment }}</div>
        <div class="timestamp">Dernière mise à jour : {{ timestamp }}</div>
    {% endif %}

    <h2>📜 Historique des Prédictions</h2>
    <table>
        <tr>
            <th>Date</th>
            <th>Sentiment</th>
            <th>Action</th>
        </tr>
        {% for i, entry in enumerate(history) %}
        <tr>
            <td>{{ entry['date'] }}</td>
            <td>{{ entry['sentiment'] }}</td>
            <td>
                <form method="POST" action="/delete/{{ i }}">
                    <button type="submit" class="delete-btn">❌</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# ====== 📡 ROUTES FLASK ======
@app.route('/', methods=['GET', 'POST'])
def home():
    sentiment = None
    timestamp = None

    if request.method == 'POST':
        sentiment = get_market_sentiment()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    history = load_history()
    
    return render_template_string(
        html_template, 
        sentiment=sentiment, 
        timestamp=timestamp, 
        history=history, 
        enumerate=enumerate  # 👈 Solution ici
    )

@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    delete_entry(index)
    return redirect(url_for('home'))

# ====== 🚀 LANCEMENT SERVEUR ======
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
