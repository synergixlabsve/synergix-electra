from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# === CONFIGURACIÓN ===
VERIFY_TOKEN = "synergix2025"

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
    if data and 'messages' in data:
        for msg in data['messages']:
            from_number = msg.get('from')
            text = msg.get('text', {}).get('body', '').strip().lower()

            if from_number and text:
                print(f"📩 {from_number}: {text}")
                responder(from_number, text)

    return jsonify({'status': 'ok'}), 200

# === RESPONDER según el mensaje recibido ===
def responder(to, text):
    # Saludos
    if any(word in text for word in ['hola', 'buenas', 'buenos', 'buen día']):
        send_whatsapp_message(to,
            "¡Hola! Soy Electra, asistente virtual de Synergix Labs – Robótica y Electrónica.\n"
            "Ofrecemos cursos vacacionales 2025:\n\n"
            "🔌 *Electrónica Básica* (7-12 años) – Del 4 al 8 de agosto\n"
            "🤖 *Electrónica con Arduino* (10-16 años) – Del 11 al 15 de agosto\n"
            "🐍 *Programación con Python* (12-17 años) – Del 18 al 22 de agosto\n\n"
            "✅ Certificado avalado por el Ateneo Eudes Navas Soto\n"
            "📍 Sector La Candelaria, Punta Cardón\n\n"
            "¿Sobre qué curso te gustaría saber más?"
        )

    # Información general
    elif any(word in text for word in ['información', 'detalles', 'cursos', 'vacacional']):
        send_whatsapp_message(to,
            "📚 *Cursos Vacacionales 2025 – Synergix Labs*\n\n"
            "1. *Electrónica Básica* (7-12 años)\n"
            "   - Fechas: 4 al 8 de agosto\n"
            "   - Horario: 3:00 p.m. a 5:00 p.m.\n"
            "   - Aprenderán: circuitos, LEDs, motores, diagramas\n\n"
            "2. *Electrónica con Arduino* (10-16 años)\n"
            "   - Fechas: 11 al 15 de agosto\n"
            "   - Aprenderán: programación básica, sensores, proyectos\n\n"
            "3. *Programación con Python* (12-17 años)\n"
            "   - Fechas: 18 al 22 de agosto\n"
            "   - Aprenderán: variables, bucles, funciones, proyectos\n\n"
            "✅ Materiales incluidos\n"
            "✅ Certificado oficial\n"
            "✅ Grupos por edad\n\n"
            "¿Te gustaría saber más sobre alguno?"
        )

    # Precio
    elif any(word in text for word in ['costo', 'precio', 'cuánto cuesta', 'ref']):
        send_whatsapp_message(to,
            "📌 *Precios 2025*\n\n"
            "• Cada curso individual: Ref. 20\n"
            "• Plan completo (3 cursos): Ref. 55 (ahorro de Ref. 5)\n\n"
            "📆 Fecha límite de pago completo: viernes 1 de agosto 2025\n\n"
            "¿Te gustaría inscribirte?"
        )

    # Materiales
    elif any(word in text for word in ['materiales', 'necesito llevar', 'traer']):
        send_whatsapp_message(to,
            "📦 *Materiales en Synergix Labs*\n\n"
            "Todos los materiales prácticos (circuitos, placas, sensores) son proporcionados por nosotros.\n\n"
            "⚠️ Los proyectos se usan en clase y no se llevan a casa, pero si deseas conservar el tuyo, "
            "puedes adquirir los componentes electrónicos por separado.\n\n"
            "💡 ¡No necesitas traer nada, excepto entusiasmo por aprender!"
        )

    # Pago
    elif any(word in text for word in ['pago', 'pagar', 'dinero', 'cancelar', 'datos de pago']):
        send_whatsapp_message(to,
            "💳 *Opciones de pago en Synergix Labs*\n\n"
            "Puedes pagar por:\n"
            "• *Pago Móvil*\n"
            "   - Banco: Banco de Venezuela\n"
            "   - Número: 0414-8912730\n"
            "   - Titular: Gemmy León\n"
            "   - Cédula: 13655511\n"
            "   - A tasa BCV\n\n"
            "• *Efectivo* (en persona en el Ateneo)\n\n"
            "📌 *Costo por curso:* Ref. 20\n"
            "📌 *Plan completo (3 cursos):* Ref. 55\n\n"
            "📆 *Fecha límite de pago completo:* viernes 1 de agosto 2025\n\n"
            "Una vez pagues, envía el comprobante por este WhatsApp para confirmar tu inscripción."
        )

    # Python
    elif any(word in text for word in ['python', 'programación']):
        send_whatsapp_message(to,
            "🐍 *Curso de Programación con Python*\n\n"
            "Ideal para adolescentes de 12 a 17 años.\n"
            "📅 Del 18 al 22 de agosto\n"
            "🕐 3:00 p.m. a 5:00 p.m.\n"
            "📍 Ateneo Eudes Navas Soto\n\n"
            "💡 Contenido:\n"
            "- Variables, bucles, condicionales\n"
            "- Listas, funciones, proyectos\n"
            "- Pensamiento lógico y creativo\n\n"
            "📱 *Requisito:* traer celular, tablet o laptop\n\n"
            "¿Te gustaría inscribir a alguien?"
        )

    # Confirmación de inscripción
    elif any(word in text for word in ['inscribir', 'registro', 'cupos', 'confirmar']):
        send_whatsapp_message(to,
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

    # Respuesta genérica
    else:
        send_whatsapp_message(to,
            "Gracias por tu mensaje. Un asesor (Gemmy León) se comunicará contigo en menos de 24 horas.\n"
            "📞 0414-8912730\n"
            "📧 synergixlabs@zohomail.com"
        )

# === Enviar mensaje a través de Z-API ===
def send_whatsapp_message(to, text):
    url = "https://api.z-api.io/instances/3E4AB848C37E70F9F1F0EA8A4730038C/token/0EC520302220C2AA697FACC8/send-text"
    payload = {
        "phone": to,
        "message": text
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print("❌ Error al enviar mensaje:", str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
