from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# === CONFIGURACIÓN ===
VERIFY_TOKEN = "synergix2025"
QWEN_API_URL = "https://qwen.ai/api/inference"

# Historial de conversaciones
conversation_history = {}

# === WEBHOOK: Verificación ===
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Error", 403

# === WEBHOOK: Recibir mensajes ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get('object'):
        for entry in data['entry']:
            for change in entry['changes']:
                value = change.get('value')
                message = value.get('messages', [{}])[0]
                from_number = message.get('from')
                text = message.get('text', {}).get('body', "").strip().lower()

                if from_number and text:
                    print(f"📩 {from_number}: {text}")

                    # Detectar si pide información
                    if any(word in text for word in ['flyer', 'temario', 'pdf', 'información', 'descargar', 'verano']):
                        send_general_flyer(from_number)
                        continue

                    if any(word in text for word in ['inscripción', 'inscribir', 'registro', 'cupos']):
                        send_registration_message(from_number)
                        continue

                    # Procesar con Qwen
                    response_text = get_qwen_response(from_number, text)
                    send_whatsapp_message(from_number, response_text)

    return jsonify({'status': 'ok'}), 200

# === Obtener respuesta de Qwen ===
def get_qwen_response(user_id, user_message):
    if user_id not in conversation_history:
        conversation_history[user_id] = [
            {"role": "system", "content": get_system_prompt()}
        ]
    conversation_history[user_id].append({"role": "user", "content": user_message})

    try:
        response = requests.post(
            QWEN_API_URL,
            json={
                "model": "qwen-max",
                "messages": conversation_history[user_id],
                "temperature": 0.7,
                "max_tokens": 500
            },
            headers={
                "Authorization": f"Bearer {os.environ.get('QWEN_API_KEY')}",
                "Content-Type": "application/json"
            }
        )
        ai_response = response.json().get("output", {}).get("text", "No pude responder.")
        conversation_history[user_id].append({"role": "assistant", "content": ai_response})
        return ai_response
    except Exception as e:
        print("❌ Error con Qwen:", str(e))
        return "Estoy teniendo un problema técnico. Intenta más tarde."

# === Enviar mensaje por WhatsApp ===
def send_whatsapp_message(to, text):
    url = "https://waba.360dialog.io/v1/messages"
    headers = {
        "D360-API-KEY": os.environ.get('ACCESS_TOKEN'),
        "Content-Type": "application/json"
    }
    payload = {
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print("❌ Error al enviar mensaje:", str(e))

# === Enviar flyer general ===
def send_general_flyer(to):
    url = "https://waba.360dialog.io/v1/messages"
    headers = {
        "D360-API-KEY": os.environ.get('ACCESS_TOKEN'),
        "Content-Type": "application/json"
    }
    # 📎 Reemplaza TU_ID_DEL_FLYER_GENERAL con el ID real de tu PDF en Google Drive
    pdf_url = "https://drive.google.com/uc?export=download&id=TU_ID_DEL_FLYER_GENERAL"
    caption = (
        "📚 ¡Aquí tienes la información de nuestros *Cursos Vacacionales 2025*!\n\n"
        "🔋 Electrónica Básica (7-12 años) – 4 al 8 ago\n"
        "🔌 Electrónica con Arduino (10-16 años) – 11 al 15 ago\n"
        "💻 Programación con Python (12-16 años) – 18 al 22 ago\n\n"
        "✅ Certificado avalado por el Ateneo Eudes Navas Soto\n"
        "📍 Sector La Candelaria, Punta Cardón\n\n"
        "¿Listo para inscribirte?\n"
        "Envía:\n"
        "• Nombre del estudiante\n"
        "• Edad\n"
        "• Curso(s) de interés\n"
        "• Teléfono de contacto"
    )
    payload = {
        "to": to,
        "type": "document",
        "document": {
            "link": pdf_url,
            "caption": caption
        }
    }
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print("❌ Error al enviar PDF:", str(e))

# === Mensaje de inscripción ===
def send_registration_message(to):
    message = (
        "📝 *¡Listo para inscribirte a Synergix Labs!* 😊\n\n"
        "Para reservar tu cupo en los cursos de verano 2025, por favor envía:\n\n"
        "1. Nombre del estudiante\n"
        "2. Edad\n"
        "3. Curso(s) de interés:\n"
        "   • Electrónica Básica (4-8 ago)\n"
        "   • Arduino (11-15 ago)\n"
        "   • Python (18-22 ago)\n"
        "4. Teléfono de contacto\n\n"
        "Un asesor se comunicará contigo en menos de 24 horas.\n\n"
        "📞 Contacto: Gemmy León\n"
        "📱 WhatsApp: 0414-8912730\n"
        "✉️ synergixlabs@zohomail.com"
    )
    send_whatsapp_message(to, message)

# === Prompt del sistema (Electra) ===
def get_system_prompt():
    return """
Eres Electra, asistente virtual de Synergix Labs – Robótica y Electrónica.
Tienes que responder con amabilidad, claridad y profesionalismo.

Información oficial (2025):
- Curso 1: Electrónica Básica (7-12 años): 4 al 8 de agosto
- Curso 2: Electrónica con Arduino (10-16 años): 11 al 15 de agosto
- Curso 3: Programación con Python (12-16 años): 18 al 22 de agosto
- Todos presenciales, en Sector La Candelaria, Punta Cardón
- Certificado avalado por el Ateneo Eudes Navas Soto

Tono: cercano, claro, educativo.
Si no sabes algo, di: "Un asesor te responderá pronto."
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
