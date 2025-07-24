from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# === CONFIGURACIÓN ===
VERIFY_TOKEN = "synergix2025"

# === WEBHOOK: Verificación (para Z-API) ===
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Forbidden", 403

# === WEBHOOK: Recibir mensajes ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    # Imprime todo el JSON recibido para depuración
    print("🔍 DATO COMPLETO RECIBIDO:", data)
    
    try:
        # Extrae el número de cualquier forma posible
        from_number = None
        
        # Busca en varias posiciones posibles
        if 'messages' in data and len(data['messages']) > 0:
            msg = data['messages'][0]
            from_number = msg.get('from')
            
            # Si no está en 'from', prueba en 'chatId' (a veces viene así)
            if not from_number and 'chatId' in msg:
                from_number = msg['chatId'].split('@')[0]
        
        # Si encontramos el número, respondemos
        if from_number:
            print(f"📞 Número detectado: {from_number}")
            
            # Forzar respuesta de prueba
            response_text = (
                "✅ ¡Hola! Soy Electra, asistente virtual de Synergix Labs.\n\n"
                "Este es un mensaje de prueba para confirmar que el sistema está funcionando.\n\n"
                "Estoy lista para responder a tus consultas sobre:\n"
                "🔌 Electrónica Básica\n"
                "🤖 Electrónica con Arduino\n"
                "🐍 Programación con Python\n\n"
                "Próximamente tendrás acceso a toda la información oficial.\n\n"
                "Gracias por tu paciencia.\n"
                "Atentamente,\n"
                "Electra – Synergix Labs"
            )
            
            # Enviar respuesta
            send_whatsapp_message(from_number, response_text)
        
        else:
            print("❌ No se pudo extraer el número del mensaje")
    
    except Exception as e:
        print("❌ Error al procesar el mensaje:", str(e))
    
    return jsonify({'status': 'ok'}), 200

# === Enviar mensaje a través de Z-API ===
def send_whatsapp_message(to, text):
    # URL directa de Z-API con tu instancia y token
    url = "https://api.z-api.io/instances/3E4AB848C37E70F9F1F0EA8A4730038C/token/0EC520302220C2AA697FACC8/send-text"
    
    payload = {
        "phone": to,
        "message": text
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"✅ Mensaje enviado a {to}")
        else:
            print(f"❌ Error al enviar mensaje: {response.status_code} - {response.text}")
    except Exception as e:
        print("❌ Excepción al enviar mensaje:", str(e))

# === Iniciar el servidor ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
