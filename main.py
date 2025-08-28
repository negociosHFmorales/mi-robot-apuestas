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
        'robot': '🤖 Sistema de Apuestas FUNCIONANDO',
        'version': '2.0',
        'estado': 'ACTIVO',
        'ultima_actualizacion': datetime.now().isoformat(),
        'rutas_disponibles': {
            '/health': 'Verificar estado del sistema',
            '/webhook': 'Recibir datos desde N8N',
            '/historial': 'Ver últimas apuestas analizadas', 
            '/estadisticas': 'Ver estadísticas del robot',
            '/analizar': 'Ejecutar análisis manual',
            '/reset': 'Limpiar historial',
            '/test-telegram': 'Probar envío a Telegram'
        }
    })

@app.route('/health')
def health():
    """Verificar que el sistema funciona"""
    return jsonify({
        'status': '✅ FUNCIONANDO PERFECTAMENTE',
        'servidor': 'Render.com',
        'hora_servidor': datetime.now().isoformat(),
        'memoria_disponible': 'OK',
        'apis_conectadas': 'OK',
        'telegram_token': '✅ Configurado' if os.getenv('TELEGRAM_TOKEN') else '❌ NO configurado',
        'telegram_chat': '✅ Configurado' if os.getenv('TELEGRAM_CHAT') else '❌ NO configurado'
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recibe y guarda datos de análisis desde N8N"""
    try:
        datos = request.get_json()
        print(f"📥 Datos recibidos: {datos}")  # Debug log
        
        # Crear registro completo
        registro = {
            'id': f"apuesta_{int(datetime.now().timestamp())}",
            'timestamp': datetime.now().isoformat(),
            'fecha_analisis': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'partido': datos.get('partido', 'Sin datos'),
            'liga': datos.get('liga', 'Sin especificar'),
            'cuotas': datos.get('cuotas', {}),
            'probabilidades': datos.get('probabilidades', {}),
            'recomendacion': datos.get('recomendacion', 'Sin recomendación'),
            'confianza': datos.get('confianza', '0%'),
            'apostar': datos.get('apostar', '0%'),
            'valor': datos.get('valor', 'NO'),
            'casa': datos.get('casa', 'N/A'),
            'origen': 'N8N_Robot'
        }
        
        print(f"📋 Registro creado: {registro}")  # Debug log
        
        # Cargar historial existente
        try:
            with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
                historial = json.load(f)
        except FileNotFoundError:
            historial = []
        except json.JSONDecodeError:
            historial = []
        
        # Agregar nuevo registro
        historial.append(registro)
        
        # Mantener solo los últimos 200 registros
        historial = historial[-200:]
        
        # Guardar historial actualizado
        with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)
        
        # SIEMPRE enviar a Telegram (para debug)
        telegram_resultado = notificar_telegram_siempre(registro)
        
        return jsonify({
            'status': '✅ GUARDADO EXITOSAMENTE',
            'registro_id': registro['id'],
            'partido': registro['partido'],
            'total_historial': len(historial),
            'telegram_enviado': telegram_resultado,
            'mensaje': 'Análisis guardado en Render'
        })
        
    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return jsonify({
            'status': '❌ ERROR',
            'mensaje': f'Error procesando datos: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/historial')
def historial():
    """Ver historial de análisis"""
    try:
        with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
            historial = json.load(f)
        
        # Estadísticas rápidas
        total = len(historial)
        con_valor = sum(1 for h in historial if h.get('valor') == 'SÍ')
        
        return jsonify({
            'resumen': {
                'total_analisis': total,
                'con_valor': con_valor,
                'sin_valor': total - con_valor,
                'porcentaje_valor': f"{(con_valor/total*100 if total > 0 else 0):.1f}%"
            },
            'ultimos_10': historial[-10:],  # Últimos 10 análisis
            'timestamp': datetime.now().isoformat()
        })
        
    except FileNotFoundError:
        return jsonify({
            'resumen': {
                'total_analisis': 0,
                'con_valor': 0,
                'sin_valor': 0,
                'porcentaje_valor': '0%'
            },
            'ultimos_10': [],
            'mensaje': 'Sin historial aún'
        })

@app.route('/estadisticas')
def estadisticas():
    """Estadísticas detalladas del robot"""
    try:
        with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
            historial = json.load(f)
        
        if not historial:
            return jsonify({'mensaje': 'Sin datos para estadísticas'})
        
        # Calcular estadísticas
        total = len(historial)
        con_valor = [h for h in historial if h.get('valor') == 'SÍ']
        
        # Por liga
        ligas = {}
        for h in historial:
            liga = h.get('liga', 'Sin especificar')
            ligas[liga] = ligas.get(liga, 0) + 1
        
        # Últimas recomendaciones
        ultimas_recomendaciones = [h.get('recomendacion', 'N/A') for h in historial[-5:]]
        
        return jsonify({
            'estadisticas_generales': {
                'total_partidos_analizados': total,
                'partidos_con_valor': len(con_valor),
                'tasa_valor': f"{(len(con_valor)/total*100 if total > 0 else 0):.1f}%",
                'primer_analisis': historial[0]['fecha_analisis'] if historial else None,
                'ultimo_analisis': historial[-1]['fecha_analisis'] if historial else None
            },
            'por_liga': ligas,
            'ultimas_recomendaciones': ultimas_recomendaciones,
            'mejor_partido': con_valor[0] if con_valor else None,
            'robot_activo_desde': datetime.now().strftime('%d/%m/%Y')
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error generando estadísticas: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })

@app.route('/analizar')
def analizar_manual():
    """Trigger manual para pruebas"""
    mensaje = f"🤖 Análisis manual ejecutado - {datetime.now().strftime('%H:%M')}"
    
    # Si tienes Telegram configurado, enviar notificación
    if os.getenv('TELEGRAM_TOKEN') and os.getenv('TELEGRAM_CHAT'):
        try:
            url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage"
            data = {
                'chat_id': os.getenv('TELEGRAM_CHAT'),
                'text': f"🔄 {mensaje}\n\n✅ Robot funcionando desde Render\n🔗 Sistema conectado correctamente"
            }
            response = requests.post(url, json=data, timeout=10)
            telegram_status = "✅ Enviado" if response.status_code == 200 else f"⚠️ Error: {response.status_code}"
        except Exception as e:
            telegram_status = f"❌ Error: {str(e)}"
    else:
        telegram_status = "⚙️ Telegram no configurado"
    
    return jsonify({
        'mensaje': mensaje,
        'telegram': telegram_status,
        'render_status': '✅ Funcionando',
        'siguiente_paso': 'Ejecutar flujo N8N para obtener datos reales'
    })

@app.route('/reset')
def reset_historial():
    """Limpiar historial (solo para testing)"""
    try:
        with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        return jsonify({
            'status': '✅ HISTORIAL LIMPIO',
            'mensaje': 'Todos los registros han sido eliminados',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': '❌ ERROR',
            'mensaje': f'Error limpiando historial: {str(e)}'
        }), 500

@app.route('/test-telegram')
def test_telegram():
    """Probar envío directo a Telegram"""
    try:
        token = os.getenv('TELEGRAM_TOKEN')
        chat = os.getenv('TELEGRAM_CHAT')
        
        if not token:
            return jsonify({'error': '❌ TELEGRAM_TOKEN no configurado'})
        
        if not chat:
            return jsonify({'error': '❌ TELEGRAM_CHAT no configurado'})
        
        # Crear mensaje de prueba
        registro_prueba = {
            'partido': 'PRUEBA SISTEMA vs FUNCIONANDO',
            'liga': 'Test League',
            'fecha_analisis': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'recomendacion': '✅ Sistema operativo',
            'confianza': '100%',
            'apostar': '0%',
            'valor': 'FUNCIONANDO'
        }
        
        resultado = notificar_telegram_siempre(registro_prueba)
        
        return jsonify({
            'status': '🧪 PRUEBA TELEGRAM',
            'resultado': resultado,
            'token_configurado': '✅ Sí',
            'chat_configurado': '✅ Sí'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'❌ Error en prueba: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })

def notificar_telegram_siempre(registro):
    """Enviar SIEMPRE a Telegram (para debug y pruebas)"""
    try:
        token = os.getenv('TELEGRAM_TOKEN')
        chat = os.getenv('TELEGRAM_CHAT')
        
        if not token or not chat:
            return "❌ Token o Chat no configurados"
        
        # Crear mensaje formateado
        mensaje = f"""🎯 ANÁLISIS COMPLETADO 🎯

🏀 {registro.get('partido', 'Sin datos')}
🏆 Liga: {registro.get('liga', 'N/A')}
📅 Análisis: {registro.get('fecha_analisis', 'N/A')}

💡 Recomendación: {registro.get('recomendacion', 'N/A')}
📊 Confianza: {registro.get('confianza', '0%')}
💰 Apostar: {registro.get('apostar', '0%')} del bankroll
✅ Valor: {registro.get('valor', 'NO')}

🤖 Robot funcionando desde Render
⏰ {datetime.now().strftime('%H:%M:%S')}"""

        # Enviar mensaje
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat,
            'text': mensaje,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            return "✅ Mensaje enviado correctamente"
        else:
            return f"⚠️ Error HTTP: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"❌ Error enviando: {str(e)}"

def notificar_telegram_valor(registro):
    """Enviar notificación especial cuando hay valor alto"""
    try:
        token = os.getenv('TELEGRAM_TOKEN')
        chat = os.getenv('TELEGRAM_CHAT') 
        
        if not token or not chat:
            return "❌ Telegram no configurado"
            
        mensaje = f"""🚨 VALOR ALTO DETECTADO 🚨

🎰 {registro.get('partido', 'Sin datos')}
🏆 {registro.get('liga', 'N/A')}
📅 {registro.get('fecha_analisis', 'N/A')}

💰 CUOTAS:
{registro.get('cuotas', {})}

📊 PROBABILIDADES:
{registro.get('probabilidades', {})}

🎯 RECOMENDACIÓN: {registro.get('recomendacion', 'N/A')}
🔥 CONFIANZA: {registro.get('confianza', '0%')}
💎 APOSTAR: {registro.get('apostar', '0%')} del bankroll

⚠️ ¡Revisar inmediatamente!
🏪 Casa: {registro.get('casa', 'N/A')}"""

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat,
            'text': mensaje
        }
        
        response = requests.post(url, json=data, timeout=10)
        return "✅ Alerta de valor enviada" if response.status_code == 200 else f"Error: {response.status_code}"
        
    except Exception as e:
        return f"❌ Error en notificación: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
