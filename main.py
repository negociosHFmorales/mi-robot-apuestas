from flask import Flask, jsonify, request
import requests
import json
from datetime import datetime
import os
import logging

app = Flask(__name__)

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CONFIGURACIÓN CRÍTICA - USAR EL PUERTO CORRECTO
PORT = int(os.environ.get('PORT', 10000))

# Variables de entorno CONSISTENTES
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT = os.getenv('TELEGRAM_CHAT')
ODDS_API_KEY = os.getenv('ODDS_API_KEY', '187f072e0b43d7193c8e2c63fc612e9a')

# Archivo para guardar historial
HISTORIAL_FILE = '/tmp/historial_apuestas.json'

@app.route('/')
def home():
    """Página principal - VERIFICACIÓN DE ESTADO"""
    return jsonify({
        'robot': '🤖 SISTEMA APUESTAS V4.0 FUNCIONANDO',
        'estado': '✅ ONLINE EN RENDER',
        'hora': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'puerto': PORT,
        'telegram': '✅ LISTO' if (TELEGRAM_TOKEN and TELEGRAM_CHAT) else '❌ FALTA CONFIG',
        'rutas_disponibles': {
            '/': 'Estado actual',
            '/health': 'Health check Render',
            '/test-telegram': 'PROBAR TELEGRAM AHORA',
            '/webhook': 'Recibir de N8N',
            '/nba': 'Obtener cuotas NBA',
            '/manual': 'Envío manual de prueba'
        }
    })

@app.route('/health')
def health():
    """Health check para Render - CRÍTICO PARA QUE NO SE APAGUE"""
    return jsonify({
        'status': 'healthy',
        'port': PORT,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/test-telegram')
def test_telegram():
    """PROBAR TELEGRAM INMEDIATAMENTE"""
    try:
        if not TELEGRAM_TOKEN:
            return jsonify({
                'error': '❌ TELEGRAM_TOKEN no está en Render',
                'solucion': 'Ve a Render > Environment > Agregar TELEGRAM_TOKEN'
            }), 400
        
        if not TELEGRAM_CHAT:
            return jsonify({
                'error': '❌ TELEGRAM_CHAT no está en Render',
                'solucion': 'Ve a Render > Environment > Agregar TELEGRAM_CHAT'
            }), 400

        mensaje = f"""🎉 SISTEMA FUNCIONANDO PERFECTAMENTE

🤖 Robot Apuestas: ✅ ACTIVO
⏰ Hora: {datetime.now().strftime('%H:%M:%S')}
🌐 Servidor: Render.com
📡 Puerto: {PORT}

✅ Listo para recibir apuestas de N8N
✅ Telegram conectado correctamente

🎯 PRÓXIMO PASO: Ejecutar flujo N8N"""

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, json={
            'chat_id': TELEGRAM_CHAT,
            'text': mensaje,
            'parse_mode': 'HTML'
        })
        
        if response.status_code == 200:
            return jsonify({
                'status': '✅ ÉXITO TOTAL',
                'mensaje': 'Telegram funcionando perfectamente',
                'revisa_telegram': 'Deberías ver el mensaje en tu chat'
            })
        else:
            return jsonify({
                'error': f'Error Telegram: {response.status_code}',
                'detalle': response.text
            }), 400
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """RECIBIR DATOS DE N8N"""
    try:
        datos = request.get_json()
        logger.info(f"Datos recibidos de N8N: {datos}")
        
        # Procesar datos de N8N
        if datos.get('tipo') == 'juego':
            mensaje = format_game_message(datos)
        else:
            mensaje = datos.get('mensaje', 'Sin datos')
        
        # Enviar a Telegram si está configurado
        if TELEGRAM_TOKEN and TELEGRAM_CHAT:
            enviar_telegram(mensaje)
        
        # Guardar en historial
        guardar_historial(datos)
        
        return jsonify({
            'status': 'success',
            'processed': True,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/nba')
def get_nba():
    """Obtener cuotas NBA directamente"""
    try:
        if not ODDS_API_KEY:
            return jsonify({'error': 'API key no configurada'}), 400
            
        url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
        params = {
            'apiKey': ODDS_API_KEY,
            'regions': 'us',
            'markets': 'h2h'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            games = response.json()
            
            if not games:
                return jsonify({
                    'mensaje': 'No hay juegos NBA disponibles',
                    'tipo': 'sin_datos'
                })
            
            # Formatear primer juego
            game = games[0]
            resultado = {
                'partido': f"{game['away_team']} @ {game['home_team']}",
                'fecha': datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00')).strftime('%d/%m %H:%M'),
                'tipo': 'juego'
            }
            
            # Agregar cuotas si existen
            if game.get('bookmakers'):
                bookmaker = game['bookmakers'][0]
                market = next((m for m in bookmaker['markets'] if m['key'] == 'h2h'), None)
                if market:
                    for outcome in market['outcomes']:
                        if outcome['name'] == game['home_team']:
                            resultado['cuotaLocal'] = outcome['price']
                        elif outcome['name'] == game['away_team']:
                            resultado['cuotaVisitante'] = outcome['price']
                    resultado['casa'] = bookmaker['title']
            
            # Enviar a Telegram si está configurado
            if TELEGRAM_TOKEN and TELEGRAM_CHAT:
                mensaje = format_game_message(resultado)
                enviar_telegram(mensaje)
            
            return jsonify(resultado)
            
        else:
            return jsonify({
                'error': f'Error API: {response.status_code}',
                'mensaje': 'No se pudieron obtener las cuotas'
            }), response.status_code
            
    except Exception as e:
        logger.error(f"Error NBA: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/manual')
def manual():
    """Envío manual de prueba"""
    try:
        datos_prueba = {
            'partido': 'Lakers @ Warriors',
            'fecha': datetime.now().strftime('%d/%m %H:%M'),
            'cuotaLocal': '2.10',
            'cuotaVisitante': '1.75',
            'casa': 'Bet365',
            'tipo': 'juego'
        }
        
        mensaje = format_game_message(datos_prueba)
        
        if TELEGRAM_TOKEN and TELEGRAM_CHAT:
            resultado = enviar_telegram(mensaje)
            return jsonify({
                'status': 'Enviado',
                'telegram': resultado,
                'datos': datos_prueba
            })
        else:
            return jsonify({
                'error': 'Telegram no configurado',
                'datos': datos_prueba
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def format_game_message(datos):
    """Formatear mensaje para Telegram"""
    mensaje = f"""🏀 **NBA HOY**

⚡ {datos.get('partido', 'Sin partido')}
📅 {datos.get('fecha', 'Sin fecha')}

💰 **Cuotas:**
• Local: {datos.get('cuotaLocal', 'N/A')}
• Visitante: {datos.get('cuotaVisitante', 'N/A')}

🏢 Casa: {datos.get('casa', 'Sistema')}
⏰ Actualizado: {datetime.now().strftime('%H:%M')}"""
    
    return mensaje

def enviar_telegram(mensaje):
    """Enviar mensaje a Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, json={
            'chat_id': TELEGRAM_CHAT,
            'text': mensaje,
            'parse_mode': 'Markdown'
        })
        
        if response.status_code == 200:
            return "✅ Enviado"
        else:
            return f"Error: {response.status_code}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def guardar_historial(datos):
    """Guardar en historial temporal"""
    try:
        # Cargar historial existente
        try:
            with open(HISTORIAL_FILE, 'r') as f:
                historial = json.load(f)
        except:
            historial = []
        
        # Agregar nuevo registro
        historial.append({
            'timestamp': datetime.now().isoformat(),
            'datos': datos
        })
        
        # Mantener solo últimos 100
        historial = historial[-100:]
        
        # Guardar
        with open(HISTORIAL_FILE, 'w') as f:
            json.dump(historial, f)
            
    except Exception as e:
        logger.error(f"Error guardando historial: {e}")

if __name__ == '__main__':
    print(f"🚀 INICIANDO EN PUERTO {PORT}")
    print(f"📡 Telegram: {'✅ Configurado' if TELEGRAM_TOKEN else '❌ Falta configurar'}")
    print(f"🌐 Servidor: Render.com")
    
    # CRÍTICO: Usar el puerto correcto
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False
    )
