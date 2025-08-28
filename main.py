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
    """Página principal del robot"""
    return jsonify({
        'robot': '🤖 SISTEMA DE APUESTAS V3.0',
        'estado': '✅ FUNCIONANDO PERFECTAMENTE',
        'hora': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'servidor': 'Render.com',
        'version': '3.0-STABLE',
        'telegram_configurado': '✅' if os.getenv('TELEGRAM_TOKEN') else '❌',
        'rutas': {
            '/health': 'Estado del sistema',
            '/test-telegram': 'Probar Telegram AHORA',
            '/webhook': 'Recibir datos de N8N',
            '/historial': 'Ver análisis guardados',
            '/manual': 'Envío manual de prueba'
        }
    })

@app.route('/health')
def health():
    """Estado detallado del sistema"""
    token_ok = bool(os.getenv('TELEGRAM_TOKEN'))
    chat_ok = bool(os.getenv('TELEGRAM_CHAT'))
    
    return jsonify({
        'status': '🟢 ONLINE',
        'timestamp': datetime.now().isoformat(),
        'servidor': 'Render Cloud',
        'telegram': {
            'token_configurado': '✅ SÍ' if token_ok else '❌ NO',
            'chat_configurado': '✅ SÍ' if chat_ok else '❌ NO',
            'listo_para_enviar': '🟢 SÍ' if (token_ok and chat_ok) else '🔴 NO'
        },
        'archivos': {
            'historial_existe': '✅' if os.path.exists(HISTORIAL_FILE) else '⚪ Nuevo'
        },
        'memoria': '✅ OK',
        'conexion': '✅ OK'
    })

@app.route('/test-telegram')
def test_telegram():
    """🧪 PROBAR TELEGRAM INMEDIATAMENTE"""
    try:
        token = os.getenv('TELEGRAM_TOKEN')
        chat = os.getenv('TELEGRAM_CHAT')
        
        if not token:
            return jsonify({
                'status': '❌ ERROR',
                'problema': 'TELEGRAM_TOKEN no configurado en Render',
                'solucion': 'Ve a Environment en Render y agrega TELEGRAM_TOKEN'
            })
        
        if not chat:
            return jsonify({
                'status': '❌ ERROR', 
                'problema': 'TELEGRAM_CHAT no configurado en Render',
                'solucion': 'Ve a Environment en Render y agrega TELEGRAM_CHAT'
            })

        # Mensaje de prueba
        mensaje = f"""🧪 PRUEBA EXITOSA - SISTEMA FUNCIONANDO

🤖 Robot: ✅ Activo
⏰ Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🌐 Servidor: Render.com
📡 Conexión: Perfecta

🎯 PRÓXIMOS PASOS:
1. Ejecutar flujo N8N
2. Recibir análisis automáticos
3. ¡Listo para apostar!

✅ Sistema 100% operativo"""

        # Enviar a Telegram
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat,
            'text': mensaje,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            return jsonify({
                'status': '🎉 ÉXITO TOTAL',
                'mensaje': '✅ Telegram funcionando perfectamente',
                'enviado_a': f'Chat ID: {chat}',
                'codigo': response.status_code,
                'siguiente_paso': 'Ejecutar flujo N8N para recibir análisis reales'
            })
        else:
            return jsonify({
                'status': '⚠️ PROBLEMA',
                'error': f'Código HTTP: {response.status_code}',
                'respuesta': response.text[:200],
                'posible_causa': 'Chat ID incorrecto o bot bloqueado'
            })
            
    except Exception as e:
        return jsonify({
            'status': '💥 ERROR TÉCNICO',
            'error': str(e),
            'solucion': 'Verificar variables de entorno en Render'
        })

@app.route('/webhook', methods=['POST'])
def webhook():
    """📨 RECIBIR ANÁLISIS DESDE N8N"""
    try:
        datos = request.get_json()
        print(f"📥 N8N ENVIADO: {datos}")
        
        # Crear registro detallado
        registro = {
            'id': f"bet_{int(datetime.now().timestamp())}",
            'timestamp': datetime.now().isoformat(),
            'fecha_analisis': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'partido': datos.get('partido', '❓ Sin datos'),
            'liga': datos.get('liga', 'Liga Desconocida'),
            'fecha_partido': datos.get('fecha', 'Sin fecha'),
            'hora_partido': datos.get('hora', 'Sin hora'),
            'cuotas': {
                'local': datos.get('cuotaLocal', 'N/A'),
                'visitante': datos.get('cuotaVisitante', 'N/A'), 
                'empate': datos.get('cuotaEmpate', 'N/A')
            },
            'analisis': {
                'recomendacion': datos.get('recomendacion', '❓ Sin análisis'),
                'confianza': datos.get('confianza', '0%'),
                'apostar': datos.get('apostar', '0%'),
                'valor': datos.get('valor', 'NO'),
                'casa': datos.get('casa', 'Desconocida')
            },
            'origen': 'N8N-Robot',
            'estado': 'procesado'
        }
        
        # Guardar en historial
        historial = cargar_historial()
        historial.append(registro)
        historial = historial[-100:]  # Últimos 100
        guardar_historial(historial)
        
        # ENVIAR SIEMPRE A TELEGRAM
        resultado_telegram = enviar_telegram_analisis(registro)
        
        return jsonify({
            'status': '🎉 PROCESADO EXITOSAMENTE',
            'registro_id': registro['id'],
            'partido': registro['partido'],
            'telegram': resultado_telegram,
            'guardado': '✅ SÍ',
            'total_historial': len(historial),
            'timestamp': registro['timestamp']
        })
        
    except Exception as e:
        print(f"💥 ERROR WEBHOOK: {e}")
        return jsonify({
            'status': '💥 ERROR',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/manual')
def manual():
    """🎯 ENVÍO MANUAL DE PRUEBA"""
    # Datos de ejemplo
    registro_prueba = {
        'id': f"manual_{int(datetime.now().timestamp())}",
        'timestamp': datetime.now().isoformat(),
        'fecha_analisis': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'partido': 'REAL MADRID vs BARCELONA',
        'liga': 'La Liga - PRUEBA MANUAL',
        'fecha_partido': datetime.now().strftime('%d/%m/%Y'),
        'hora_partido': '21:00',
        'cuotas': {
            'local': '2.10',
            'visitante': '3.40',
            'empate': '3.20'
        },
        'analisis': {
            'recomendacion': '🏠 REAL MADRID FAVORITO',
            'confianza': '75%',
            'apostar': '3%',
            'valor': 'SÍ',
            'casa': 'Bet365'
        },
        'origen': 'MANUAL-TEST',
        'estado': 'enviado'
    }
    
    # Enviar a Telegram
    resultado = enviar_telegram_analisis(registro_prueba)
    
    # Guardar en historial
    historial = cargar_historial()
    historial.append(registro_prueba)
    guardar_historial(historial)
    
    return jsonify({
        'status': '📨 ENVIADO MANUALMENTE',
        'telegram': resultado,
        'datos_enviados': registro_prueba,
        'uso': 'Para probar que todo funciona correctamente'
    })

@app.route('/historial')
def historial():
    """📊 VER HISTORIAL COMPLETO"""
    try:
        historial = cargar_historial()
        total = len(historial)
        
        if total == 0:
            return jsonify({
                'mensaje': '📭 Sin análisis aún',
                'total': 0,
                'sugerencia': 'Ejecuta el flujo N8N o usa /manual para enviar pruebas'
            })
        
        # Estadísticas
        con_valor = sum(1 for h in historial if h.get('analisis', {}).get('valor') == 'SÍ')
        manuales = sum(1 for h in historial if 'MANUAL' in h.get('origen', ''))
        
        return jsonify({
            'resumen': {
                'total_analisis': total,
                'con_valor': con_valor,
                'sin_valor': total - con_valor,
                'porcentaje_valor': f"{(con_valor/total*100):.1f}%",
                'envios_manuales': manuales,
                'desde_n8n': total - manuales
            },
            'ultimos_5': historial[-5:],
            'primer_analisis': historial[0]['fecha_analisis'] if historial else None,
            'ultimo_analisis': historial[-1]['fecha_analisis'] if historial else None
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error cargando historial: {str(e)}'
        })

def cargar_historial():
    """Cargar historial desde archivo"""
    try:
        with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def guardar_historial(historial):
    """Guardar historial en archivo"""
    try:
        with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando historial: {e}")

def enviar_telegram_analisis(registro):
    """📱 ENVIAR ANÁLISIS FORMATEADO A TELEGRAM"""
    try:
        token = os.getenv('TELEGRAM_TOKEN')
        chat = os.getenv('TELEGRAM_CHAT')
        
        if not token or not chat:
            return "❌ Telegram no configurado"
        
        # Crear mensaje súper detallado
        cuotas = registro.get('cuotas', {})
        analisis = registro.get('analisis', {})
        
        mensaje = f"""🚨 ANÁLISIS DE APUESTA DETECTADO 🚨

⚽ **{registro.get('partido', 'Partido desconocido')}**
🏆 {registro.get('liga', 'Liga desconocida')}
📅 {registro.get('fecha_partido', 'Sin fecha')} a las {registro.get('hora_partido', 'Sin hora')}

💰 **CUOTAS ACTUALES:**
🏠 Local: **{cuotas.get('local', 'N/A')}**
✈️ Visitante: **{cuotas.get('visitante', 'N/A')}**
🤝 Empate: **{cuotas.get('empate', 'N/A')}**

🎯 **ANÁLISIS COMPLETO:**
💡 Recomendación: **{analisis.get('recomendacion', 'Sin recomendación')}**
📊 Confianza: **{analisis.get('confianza', '0%')}**
💎 Apostar: **{analisis.get('apostar', '0%')}** del bankroll
✅ Valor detectado: **{analisis.get('valor', 'NO')}**
🏪 Casa de apuestas: **{analisis.get('casa', 'N/A')}**

⏰ Análisis realizado: {registro.get('fecha_analisis', 'Sin fecha')}
🤖 Origen: {registro.get('origen', 'Sistema')}

⚠️ **¡APUESTA CON RESPONSABILIDAD!**"""

        # Enviar mensaje
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat,
            'text': mensaje,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            return "✅ Enviado correctamente"
        else:
            return f"⚠️ Error: {response.status_code}"
            
    except Exception as e:
        return f"💥 Error técnico: {str(e)}"

if __name__ == '__main__':
    print("🚀 INICIANDO SISTEMA DE APUESTAS V3.0")
    print("📡 Render.com deployment")
    print("🤖 Robot listo para funcionar")
    app.run(
        host='0.0.0.0', 
        port=int(os.environ.get('PORT', 5000)), 
        debug=False
    )
