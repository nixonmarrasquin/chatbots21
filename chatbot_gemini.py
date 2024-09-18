import google.generativeai as genai

# Configura la API key de Gemini
genai.configure(api_key="AIzaSyA-QJQVpjhveWOTvoiBLttVOqgM2h-XI14")

# Inicializa el modelo
model = genai.GenerativeModel('gemini-pro')

# Información sobre tu negocio
BUSINESS_INFO = """
Nombre del negocio: Electrónica Siglo 21
Descripción: Mayorista de Tecnología
Productos/Servicios: Productos de tecnología, como electrodomésticos, computadoras, software, hardware
Horario de atención: Lunes a Viernes de 9am a 6pm
Ubicación: En Guayaquil en Cdla. La Garzota, Av. Isidro Ayora entre calle 15E NE y Av. 3A NE - En Quito estamos ubicados en Complejo Termikon Carapungo Av. capitán Giovanni Calles y Viteri Complejo Loginet bodega B12 
Teléfono: (04) 373-2121
Email de Soporte: paginaweb@siglo21.net
Políticas: 
Envios gratis: Si 
Ser cliente / ser distribuidor: Para ser cliente de Siglo 21 debe llenar el formulario en la sección de Ser distribuidor para luego poder calificarlo como cliente. Puede ingresar al siguiente enlace https://siglo21.net/solicitud-de-registro/
"""

def interactuar_con_chatbot(user_input):
    try:
        # Crea un prompt que incluye la información del negocio y la pregunta del usuario
        prompt = f"""Eres un asistente virtual para el siguiente negocio. 
        Información del negocio:
        {BUSINESS_INFO}
        
        Instrucciones:
        1. Responde únicamente a preguntas relacionadas con la información proporcionada sobre el negocio.
        2. Si la pregunta no está relacionada con el negocio, responde cortésmente que solo puedes proporcionar información sobre el negocio.
        3. Sé conciso y directo en tus respuestas.
        4. Responde únicamente en español.
        5. No respondas con groserías ni con faltas de respeto
        Pregunta del cliente: {user_input}

        Respuesta:"""

        # Genera la respuesta usando Gemini
        response = model.generate_content(prompt)
        chatbot_reply = response.text.strip()

        #print(f"Respuesta del chatbot: {chatbot_reply}")
        return chatbot_reply
    except Exception as e:
        print(f"Error: {str(e)}")
        return f'Error al procesar la solicitud: {str(e)}'

if __name__ == "__main__":
    while True:
        pregunta_usuario = input("Usuario: ")
        if pregunta_usuario.lower() == 'salir':
            break
        respuesta_chatbot = interactuar_con_chatbot(pregunta_usuario)
        print("Chatbot:", respuesta_chatbot) 