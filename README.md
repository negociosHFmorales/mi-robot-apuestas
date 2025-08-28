# 🤖 SISTEMA DE APUESTAS AUTOMÁTICO V3.0

## 🎯 ¿QUÉ HACE ESTE SISTEMA?

✅ **Obtiene cuotas de deportes** desde APIs automáticamente  
✅ **Analiza las mejores oportunidades** de apuesta  
✅ **Te envía alertas a Telegram** cuando encuentra valor  
✅ **Guarda historial** de todos los análisis  
✅ **Funciona 24/7** en la nube (Render.com)  

## 🚀 DESPLIEGUE EN RENDER.COM

### 1. **Conectar GitHub a Render:**
- Ve a [render.com](https://render.com)
- Crea cuenta gratuita
- "New" → "Web Service" 
- Conecta tu repositorio de GitHub
- Selecciona este repo

### 2. **Configuración en Render:**
```bash
Build Command: pip install -r requirements.txt
Start Command: gunicorn main:app
Environment: Python 3
```

### 3. **Variables de Entorno OBLIGATORIAS:**
```
TELEGRAM_TOKEN = 1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT = 123456789
```

## 🤖 CONFIGURACIÓN DEL BOT DE TELEGRAM

### 1. **Crear Bot:**
1. Busca `@BotFather` en Telegram
2. Envía: `/newbot`
3. Nombre: `Mi Robot de Apuestas`
4. Username: `mi_robot_apuestas_bot`
5. **Copia el TOKEN** que te da

### 2. **Obtener tu Chat ID:**
1. Envía `/start` a tu bot
2. Ve a: `https://api.telegram.org/bot[TU_TOKEN]/getUpdates`
3. Busca: `"chat":{"id":123456789}`
4. **Copia ese número**

## 🔧 RUTAS DEL SISTEMA

Una vez desplegado en Render, tendrás estas rutas:

| Ruta | Función | Cuándo usarla |
|------|---------|---------------|
| `/` | Estado general | Para ver si funciona |
| `/health` | Estado detallado | Para debug |
| `/test-telegram` | **🧪 PROBAR TELEGRAM** | **USAR PRIMERO** |
| `/manual` | Envío manual | Para probar análisis |
| `/historial` | Ver análisis pasados | Para revisar resultados |
| `/webhook` | Recibir de N8N | Automático |

## ✅ VERIFICACIÓN PASO A PASO

### **Paso 1 - Render funcionando:**
```
https://tu-app.onrender.com/
```
Debe devolver: `"robot": "🤖 SISTEMA DE APUESTAS V3.0"`

### **Paso 2 - Telegram configurado:**
```
https://tu-app.onrender.com/test-telegram
```
Debe devolver: `"status": "🎉 ÉXITO TOTAL"`

### **Paso 3 - Envío manual:**
```
https://tu-app.onrender.com/manual
```
Debe enviarte un ejemplo a Telegram

## 🔄 INTEGRACIÓN CON N8N

Este sistema recibe datos desde N8N en la ruta `/webhook`.

**N8N debe enviar:**
```json
{
  "partido": "Real Madrid vs Barcelona",
  "liga": "La Liga",
  "fecha": "25/08/2025",
  "hora": "21:00",
  "cuotaLocal": "2.10",
  "cuotaVisitante": "3.40", 
  "cuotaEmpate": "3.20",
  "recomendacion": "🏠 Real Madrid favorito",
  "confianza": "75%",
  "apostar": "3%",
  "valor": "SÍ",
  "casa": "Bet365"
}
```

## 🚨 SOLUCIÓN DE PROBLEMAS

### **❌ "Telegram no configurado"**
- Verifica TELEGRAM_TOKEN en Render
- Verifica TELEGRAM_CHAT en Render
- Prueba `/test-telegram`

### **❌ "No recibo mensajes"**
- Bot bloqueado → Desbloquear en Telegram
- Chat ID incorrecto → Usar `/getUpdates`
- Token incorrecto → Crear nuevo bot

### **❌ "App no responde"** 
- Render dormido → Hacer ping cada 10 min
- Error en código → Ver logs en Render
- Variables faltantes → Revisar Environment

## 📊 ESTADÍSTICAS

El sistema guarda:
- ✅ Todos los análisis recibidos
- ✅ Historial de cuotas
- ✅ Recomendaciones enviadas
- ✅ Porcentaje de aciertos
- ✅ Mejores oportunidades

## 🔐 SEGURIDAD

- 🔒 **Tokens privados** (solo en variables de entorno)
- 🔒 **Sin API keys en código**
- 🔒 **Historial local** (no se comparte)
- 🔒 **HTTPS** obligatorio en Render

## 🎯 PRÓXIMOS PASOS

1. **Despliega en Render** ✅
2. **Configura Telegram** ✅
3. **Prueba `/test-telegram`** ✅
4. **Configura N8N** (siguiente paso)
5. **¡Recibe alertas automáticas!** 🎉

---

**💡 TIP:** Usa `/manual` para enviar análisis de prueba mientras configuras N8N.

**⚠️ IMPORTANTE:** Siempre apuesta con responsabilidad. Este es un sistema de análisis, no garantiza ganancias.# mi-robot-apuestas
