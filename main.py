from flask import Flask, jsonify
import requests
from config import *

app = Flask(__name__)

@app.route('/')
def home():
    """Página principal"""
    return jsonify({'mensaje': '🤖 Robot de Apuestas funcionando!'})

@app.route('/health')
def health():
    """Para verificar que funciona"""
    return jsonify({'status': 'funcionando!'})

@app.route('/analizar')
def analizar_partidos():
    """Analiza partidos de hoy"""
    
    # Por ahora, solo envía un mensaje de prueba
    mensaje = "🎯 Robot funcionando!\nAnalizando partidos..."
    
    # Enviar mensaje a Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT,
        'text': mensaje
    }
    requests.post(url, json=data)
    
    return jsonify({'mensaje': 'Análisis enviado!'})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
