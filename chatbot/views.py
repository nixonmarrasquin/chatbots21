from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.utils import timezone
from .models import CabeceraChat, DetalleChat
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
Ubicación: Guayaquil Cdla. La Garzota...
Contacto: 099999999
Políticas importantes: Envios gratis
"""

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        user_input = request.POST.get('message')
        
        if not user_input:
            return JsonResponse({'error': 'No message provided'}, status=400)

        try:
            # Verifica si hay un idCabeceraChat en la sesión
            cabecera_id = request.session.get('cabecera_id')

            if cabecera_id:
                try:
                    cabecera = CabeceraChat.objects.get(idCabeceraChat=cabecera_id)
                    print(f"Usando cabecera existente de la sesión: {cabecera_id}")
                except CabeceraChat.DoesNotExist:
                    return JsonResponse({'error': 'CabeceraChat not found'}, status=404)
            else:
                # Si no hay cabecera en la sesión, crea una nueva cabecera
                cabecera = CabeceraChat.objects.create(user="user", fecha=timezone.now())
                request.session['cabecera_id'] = cabecera.idCabeceraChat  # Almacena el ID en la sesión
                cabecera_id = cabecera.idCabeceraChat
                print(f"Nueva cabecera creada: {cabecera_id} y almacenada en la sesión")

            # Guarda el mensaje del usuario en DetalleChat
            DetalleChat.objects.create(
                idCabeceraChat=cabecera,
                mensaje=user_input,
                idTipo='1',  # 1 para el mensaje del usuario
                fechaMensaje=timezone.now()
            )
            print(f"Mensaje del usuario guardado: {user_input}")

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
            chatbot_reply = response.text

            # Guarda la respuesta del chatbot en DetalleChat
            DetalleChat.objects.create(
                idCabeceraChat=cabecera,
                mensaje=chatbot_reply,
                idTipo='0',  # 0 para la respuesta del chatbot
                fechaMensaje=timezone.now()
            )
            print(f"Respuesta del chatbot guardada: {chatbot_reply}")
            
            return JsonResponse({'reply': chatbot_reply, 'cabecera_id': cabecera_id})
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'error': f'Error al procesar la solicitud: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def chatbot_page(request):
    return render(request, 'chatbot.html')
