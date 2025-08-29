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
            '/test-webhook': 'SIMULAR WEBHOOK N8N',
            '/webhook': 'Recibir de N8N',
            '/nba': 'Obtener cuotas NBA',
            '/manual': 'Envío manual de prueba',
            '/historial': 'Ver últimos análisis'
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

@app.route('/test-webhook', methods=['GET', 'POST'])
def test_webhook():
    """Simular webhook de N8N para pruebas"""
    try:
        # Simular exactamente lo que N8N enviaría
        datos_simulados = {
            'partido': 'Boston Celtics @ Miami Heat',
            'liga': 'NBA - Temporada Regular',
            'fecha': datetime.now().strftime('%d/%m/%Y'),
            'hora': '20:30',
            'cuotaLocal': '1.85',
            'cuotaVisitante': '2.05',
            'cuotaEmpate': 'N/A',
            'recomendacion': '🏠 Miami Heat ligero favorito',
            'confianza': '65%',
            'apostar': '1.5%',
            'valor': 'POSIBLE',
            'casa': 'DraftKings'
        }
        
        # Crear el mismo mensaje que el webhook real
        mensaje = f"""🚨 ANÁLISIS DE APUESTA DETECTADO 🚨

⚽ {datos_simulados.get('partido')}
🏆 {datos_simulados.get('liga')}
📅 {datos_simulados.get('fecha')} a las {datos_simulados.get('hora')}

💰 **CUOTAS ACTUALES:**
🏠 Local: {datos_simulados.get('cuotaLocal')}
✈️ Visitante: {datos_simulados.get('cuotaVisitante')}
🤝 Empate: {datos_simulados.get('cuotaEmpate')}

🎯 **ANÁLISIS COMPLETO:**
💡 Recomendación: {datos_simulados.get('recomendacion')}
📊 Confianza: {datos_simulados.get('confianza')}
💎 Apostar: {datos_simulados.get('apostar')} del bankroll
✅ Valor detectado: {datos_simulados.get('valor')}
🏪 Casa de apuestas: {datos_simulados.get('casa')}

⏰ Análisis realizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🤖 Origen: TEST-WEBHOOK

⚠️ ¡APUESTA CON RESPONSABILIDAD!"""
        
        # Enviar a Telegram
        if TELEGRAM_TOKEN and TELEGRAM_CHAT:
            resultado = enviar_telegram(mensaje)
            guardar_historial(datos_simulados)
            
            return jsonify({
                'status': '✅ TEST EXITOSO',
                'mensaje': 'Webhook simulado correctamente',
                'telegram': resultado,
                'revisa': 'Mira tu Telegram ahora',
                'datos_enviados': datos_simulados
            })
        else:
            return jsonify({
                'error': 'Telegram no configurado',
                'datos_simulados': datos_simulados
            })
            
    except Exception as e:
        logger.error(f"Error test webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """RECIBIR DATOS DE N8N"""
    try:
        datos = request.get_json()
        logger.info(f"Datos recibidos de N8N: {datos}")
        
        # Crear mensaje formateado para análisis completo
        mensaje = f"""🚨 ANÁLISIS DE APUESTA DETECTADO 🚨

⚽ {datos.get('partido', '❓ Sin datos')}
🏆 {datos.get('liga', 'Liga Desconocida')}
📅 {datos.get('fecha', 'Sin fecha')} a las {datos.get('hora', 'Sin hora')}

💰 **CUOTAS ACTUALES:**
🏠 Local: {datos.get('cuotaLocal', 'N/A')}
✈️ Visitante: {datos.get('cuotaVisitante', 'N/A')}
🤝 Empate: {datos.get('cuotaEmpate', 'N/A')}

🎯 **ANÁLISIS COMPLETO:**
💡 Recomendación: {datos.get('recomendacion', '❓ Sin análisis')}
📊 Confianza: {datos.get('confianza', '0%')}
💎 Apostar: {datos.get('apostar', '0%')} del bankroll
✅ Valor detectado: {datos.get('valor', 'NO')}
🏪 Casa de apuestas: {datos.get('casa', 'Desconocida')}

⏰ Análisis realizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🤖 Origen: N8N-Robot

⚠️ ¡APUESTA CON RESPONSABILIDAD!"""
        
        # Enviar a Telegram
        if TELEGRAM_TOKEN and TELEGRAM_CHAT:
            resultado = enviar_telegram(mensaje)
            logger.info(f"Telegram resultado: {resultado}")
        
        # Guardar en historial
        guardar_historial(datos)
        
        return jsonify({
            'status': 'success',
            'processed': True,
            'telegram_sent': True,
            'data_received': datos,
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
                mensaje = "❌ No hay juegos NBA disponibles en este momento"
                if TELEGRAM_TOKEN and TELEGRAM_CHAT:
                    enviar_telegram(mensaje)
                return jsonify({
                    'mensaje': 'No hay juegos NBA disponibles',
                    'tipo': 'sin_datos'
                })
            
            # Formatear primer juego
            game = games[0]
            fecha_juego = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
            
            datos = {
                'partido': f"{game['away_team']} @ {game['home_team']}",
                'liga': 'NBA',
                'fecha': fecha_juego.strftime('%d/%m/%Y'),
                'hora': fecha_juego.strftime('%H:%M'),
                'tipo': 'juego'
            }
            
            # Agregar cuotas si existen
            if game.get('bookmakers'):
                bookmaker = game['bookmakers'][0]
                market = next((m for m in bookmaker['markets'] if m['key'] == 'h2h'), None)
                if market:
                    for outcome in market['outcomes']:
                        if outcome['name'] == game['home_team']:
                            datos['cuotaLocal'] = str(outcome['price'])
                        elif outcome['name'] == game['away_team']:
                            datos['cuotaVisitante'] = str(outcome['price'])
                    datos['casa'] = bookmaker['title']
            
            # Crear mensaje y enviar
            mensaje = f"""🏀 **NBA - CUOTAS EN VIVO**

⚡ {datos.get('partido')}
📅 {datos.get('fecha')} a las {datos.get('hora')}

💰 **Cuotas:**
🏠 Local: {datos.get('cuotaLocal', 'N/A')}
✈️ Visitante: {datos.get('cuotaVisitante', 'N/A')}

🏪 Casa: {datos.get('casa', 'Sistema')}
⏰ Actualizado: {datetime.now().strftime('%H:%M')}"""
            
            if TELEGRAM_TOKEN and TELEGRAM_CHAT:
                enviar_telegram(mensaje)
            
            return jsonify(datos)
            
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
    """Envío manual de prueba con datos completos"""
    try:
        # Simular datos exactos que enviaría N8N
        datos_prueba = {
            'partido': 'Los Angeles Lakers @ Golden State Warriors',
            'liga': 'NBA - Temporada Regular',
            'fecha': datetime.now().strftime('%d/%m/%Y'),
            'hora': '21:00',
            'cuotaLocal': '2.10',
            'cuotaVisitante': '1.75',
            'cuotaEmpate': 'N/A',
            'recomendacion': '✈️ Lakers FAVORITO CLARO',
            'confianza': '75%',
            'apostar': '2%',
            'valor': 'SÍ',
            'casa': 'Bet365'
        }
        
        # Usar el mismo formato que el webhook
        mensaje = f"""🚨 ANÁLISIS DE APUESTA DETECTADO 🚨

⚽ {datos_prueba.get('partido')}
🏆 {datos_prueba.get('liga')}
📅 {datos_prueba.get('fecha')} a las {datos_prueba.get('hora')}

💰 **CUOTAS ACTUALES:**
🏠 Local: {datos_prueba.get('cuotaLocal')}
✈️ Visitante: {datos_prueba.get('cuotaVisitante')}
🤝 Empate: {datos_prueba.get('cuotaEmpate')}

🎯 **ANÁLISIS COMPLETO:**
💡 Recomendación: {datos_prueba.get('recomendacion')}
📊 Confianza: {datos_prueba.get('confianza')}
💎 Apostar: {datos_prueba.get('apostar')} del bankroll
✅ Valor detectado: {datos_prueba.get('valor')}
🏪 Casa de apuestas: {datos_prueba.get('casa')}

⏰ Análisis realizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🤖 Origen: PRUEBA-MANUAL

⚠️ ¡APUESTA CON RESPONSABILIDAD!"""
        
        if TELEGRAM_TOKEN and TELEGRAM_CHAT:
            resultado = enviar_telegram(mensaje)
            guardar_historial(datos_prueba)
            return jsonify({
                'status': '✅ ENVIADO CORRECTAMENTE',
                'telegram': resultado,
                'mensaje': 'Revisa tu Telegram, deberías ver el análisis completo',
                'datos_enviados': datos_prueba
            })
        else:
            return jsonify({
                'error': 'Telegram no configurado',
                'solucion': 'Configura TELEGRAM_TOKEN y TELEGRAM_CHAT en Render'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/historial')
def historial():
    """Ver historial de análisis"""
    try:
        # Cargar historial
        try:
            with open(HISTORIAL_FILE, 'r') as f:
                historial = json.load(f)
        except:
            historial = []
        
        if not historial:
            return jsonify({
                'mensaje': 'No hay análisis guardados todavía',
                'total': 0
            })
        
        # Devolver últimos 10
        return jsonify({
            'total': len(historial),
            'ultimos_10': historial[-10:],
            'mensaje': f'Mostrando últimos {min(10, len(historial))} análisis'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def enviar_telegram(mensaje):
    """Enviar mensaje a Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, json={
            'chat_id': TELEGRAM_CHAT,
            'text': mensaje,
            'parse_mode': 'Markdown'
        }, timeout=10)
        
        if response.status_code == 200:
            return "✅ Enviado correctamente"
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
        registro = {
            'timestamp': datetime.now().isoformat(),
            'fecha': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'datos': datos
        }
        historial.append(registro)
        
        # Mantener solo últimos 100
        historial = historial[-100:]
        
        # Guardar
        with open(HISTORIAL_FILE, 'w') as f:
            json.dump(historial, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error guardando historial: {e}")

if __name__ == '__main__':
    print(f"🚀 INICIANDO EN PUERTO {PORT}")
    print(f"📡 Telegram: {'✅ Configurado' if TELEGRAM_TOKEN else '❌ Falta configurar'}")
    print(f"🌐 Servidor: Render.com")
    print("📋 Rutas disponibles:")
    print("  - / : Estado del sistema")
    print("  - /test-telegram : Probar Telegram")
    print("  - /test-webhook : Simular webhook")
    print("  - /manual : Envío manual")
    print("  - /nba : Cuotas NBA en vivo")
    print("  - /webhook : Recibir de N8N")
    print("  - /historial : Ver últimos análisis")
    
    # CRÍTICO: Usar el puerto correcto
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False
    )
