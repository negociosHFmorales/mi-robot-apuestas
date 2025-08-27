from flask import Flask, jsonify, request
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

# Archivo para guardar historial
HISTORIAL_FILE = 'historial_apuestas.json'

@app.route('/')
def home():
    """Página principal"""
    return jsonify({
        'mensaje': '🤖 Robot de Apuestas funcionando!',
        'rutas': {
            '/health': 'Estado del sistema',
            '/webhook': 'Recibe datos de N8N',
            '/historial': 'Ver historial de apuestas',
            '/estadisticas': 'Ver estadísticas'
        }
    })

@app.route('/health')
def health():
    """Para verificar que funciona"""
    return jsonify({
        'status': 'funcionando!',
        'hora': datetime.now().isoformat()
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recibe datos de N8N y los guarda"""
    try:
        datos = request.get_json()
        
        # Crear registro
        registro = {
            'fecha': datetime.now().isoformat(),
            'partido': datos.get('partido', 'Sin datos'),
            'cuotas': datos.get('cuotas', {}),
            'probabilidades': datos.get('probabilidades', {}),
            'recomendacion': datos.get('recomendacion', ''),
            'confianza': datos.get('confianza', '0%'),
            'apostar': datos.get('apostar', '0%')
        }
        
        # Cargar historial existente
        try:
            with open(HISTORIAL_FILE, 'r') as f:
                historial = json.load(f)
        except:
            historial = []
        
        # Agregar nuevo registro
        historial.append(registro)
        
        # Guardar (mantener solo últimos 100)
        with open(HISTORIAL_FILE, 'w') as f:
            json.dump(historial[-100:], f, indent=2)
        
        return jsonify({
            'status': 'guardado',
            'registro': registro
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'mensaje': str(e)
        }), 500

@app.route('/historial')
def historial():
    """Ver historial de apuestas"""
    try:
        with open(HISTORIAL_FILE, 'r') as f:
            historial = json.load(f)
        
        return jsonify({
            'total': len(historial),
            'apuestas': historial[-10:]  # Últimas 10
        })
    except:
        return jsonify({
            'total': 0,
            'apuestas': []
        })

@app.route('/estadisticas')
def estadisticas():
    """Ver estadísticas del sistema"""
    try:
        with open(HISTORIAL_FILE, 'r') as f:
            historial = json.load(f)
        
        total = len(historial)
        con_apuesta = sum(1 for h in historial if h.get('apostar', '0%') != '0%')
        
        return jsonify({
            'total_analisis': total,
            'partidos_con_valor': con_apuesta,
            'porcentaje_valor': f"{(con_apuesta/total*100 if total > 0 else 0):.1f}%",
            'ultimo_analisis': historial[-1] if historial else None
        })
    except:
        return jsonify({
            'total_analisis': 0,
            'partidos_con_valor': 0,
            'porcentaje_valor': '0%',
            'ultimo_analisis': None
        })

@app.route('/analizar')
def analizar_partidos():
    """Endpoint manual para pruebas"""
    mensaje = "🎯 Análisis manual ejecutado"
    
    # Opcional: enviar a Telegram si tienes las variables
    if os.getenv('TELEGRAM_TOKEN') and os.getenv('TELEGRAM_CHAT'):
        url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage"
        data = {
            'chat_id': os.getenv('TELEGRAM_CHAT'),
            'text': mensaje
        }
        requests.post(url, json=data)
    
    return jsonify({'mensaje': mensaje})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
