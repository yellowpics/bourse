import requests
from flask import Flask, request, render_template_string
from datetime import datetime
import os

# ====== 🔑 CONFIGURATION PERPLEXITY ======
PERPLEXITY_API_KEY = "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"
API_URL = "https://api.perplexity.ai/chat/completions"
PROMPT_FILE = "last_prompt.txt"

# ====== 🌐 APPLICATION FLASK ======
app = Flask(__name__)

# ====== 🧠 FONCTIONS DE MÉMOIRE POUR LE PROMPT ======
def save_last_prompt(prompt):
    """Enregistre le dernier prompt dans un fichier."""
    with open(PROMPT_FILE, "w") as file:
        file.write(prompt)

def load_last_prompt():
    """Lit le dernier prompt enregistré."""
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r") as file:
            return file.read().strip()
    return ""

# ====== 📊 FONCTION POUR RÉCUPÉRER LE SENTIMENT ======
def get_market_sentiment(custom_prompt):
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = custom_prompt if custom_prompt else (
        "Donne UNIQUEMENT le sentiment du marché américain aujourd’hui (S&P500, Nasdaq) "
        "sous la forme : Bullish, Bearish ou Neutral. Réponds par UN SEUL MOT."
    )

    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "Tu es un expert financier."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 80,
        "temperature": 0.0
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            return f"Erreur API ({response.status_code})"

        result = response.json()
        sentiment = result["choices"][0]["message"]["content"].strip()
        return sentiment
    except Exception as e:
        return f"Erreur : {e}"

# ====== 🌐 PAGE HTML DYNAMIQUE AVEC INPUT PROMPT ======
html_template = """
<!DOCTYPE html>
<html lang="en">
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
            color: {% if sentiment == 'Bullish' %}'#4CAF50'{% elif sentiment == 'Bearish' %}'#E74C3C'{% else %}'#3498DB'{% endif %};
        }
        .timestamp {
            font-size: 20px;
            color: #555;
        }
        form {
            margin-bottom: 30px;
        }
        input[type="text"] {
            font-size: 18px;
            padding: 10px;
            width: 60%;
            margin: 10px 0;
            border-radius: 5px;
            border: 1px solid #ccc;
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
    </style>
</head>
<body>
    <h1>📊 Sentiment du Marché (S&P500 & Nasdaq)</h1>

    <!-- FORMULAIRE POUR LE PROMPT PERSONNALISÉ -->
    <form method="POST" action="/">
        <input type="text" name="custom_prompt" placeholder="Tape ton prompt ici" value="{{ last_prompt }}" required>
        <br>
        <button type="submit">📊 Lancer l'analyse</button>
    </form>

    {% if sentiment %}
        <div class="sentiment">{{ sentiment }}</div>
        <div class="timestamp">Dernière mise à jour : {{ timestamp }}</div>
    {% endif %}
</body>
</html>
"""

# ====== 📡 ROUTE PRINCIPALE ======
@app.route('/', methods=['GET', 'POST'])
def home():
    sentiment = None
    timestamp = None

    # Charge le dernier prompt enregistré
    last_prompt = load_last_prompt()

    if request.method == 'POST':
        custom_prompt = request.form.get('custom_prompt')
        save_last_prompt(custom_prompt)  # Enregistre le nouveau prompt
        sentiment = get_market_sentiment(custom_prompt)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template_string(html_template, sentiment=sentiment, timestamp=timestamp, last_prompt=last_prompt)

# ====== 🚀 LANCEMENT SERVEUR ======
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

