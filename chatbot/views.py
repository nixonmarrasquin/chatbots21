from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.utils import timezone
from django.db import connections
from .models import CabeceraChat, DetalleChat, CodigoOTP
import google.generativeai as genai
import random
import string
import os


BUSINESS_INFO_FILE_PATH = 'C:/Users/Administrador/Desktop/chatbot_project/chatbot/static/chatbot/business_info.txt'
genai.configure(api_key="AIzaSyA-QJQVpjhveWOTvoiBLttVOqgM2h-XI14")
model = genai.GenerativeModel('gemini-pro')

def load_business_info():
    try:
        with open(BUSINESS_INFO_FILE_PATH, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "Información del negocio no disponible."
    
def generate_otp():
    return ''.join(random.choices(string.digits, k=4))

def get_client_name(codigo_cliente):
    with connections['default'].cursor() as cursor:
        # Si el código comienza con "C", lo quitamos
        if codigo_cliente.startswith('C'):
            codigo_cliente = codigo_cliente[1:]
        
        cursor.execute("""
            SELECT CardName 
            FROM webs2123.s21_users 
            WHERE CardCode = %s OR CardCode = %s
        """, [codigo_cliente, 'C' + codigo_cliente])
        result = cursor.fetchone()
        return result[0] if result else None

@csrf_exempt
@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        user_input = request.POST.get('message')
        
        if not user_input:
            return JsonResponse({'error': 'No message provided'}, status=400)

        try:
            # Cargar la información del negocio desde el archivo
            business_info = load_business_info()

            cabecera_id = request.session.get('cabecera_id')
            conversation_state = request.session.get('conversation_state', 'initial')
            otp_attempts = request.session.get('otp_attempts', 0)  # Contador de intentos fallidos de OTP

            if not cabecera_id or conversation_state == 'initial':
                cabecera = CabeceraChat.objects.create(user="user", fecha=timezone.now())
                request.session['cabecera_id'] = cabecera.idCabeceraChat
                cabecera_id = cabecera.idCabeceraChat
                # Enviar mensaje inicial
                chatbot_reply = "Hola, ¿eres cliente de Siglo 21?"
                request.session['conversation_state'] = 'waiting_for_client_status'
                DetalleChat.objects.create(
                    idCabeceraChat=cabecera,
                    mensaje=chatbot_reply,
                    idTipo='0',
                    fechaMensaje=timezone.now()
                )
                return JsonResponse({'reply': chatbot_reply, 'cabecera_id': cabecera_id})
            else:
                cabecera = CabeceraChat.objects.get(idCabeceraChat=cabecera_id)
            
            # Guarda el mensaje del usuario
            DetalleChat.objects.create(
                idCabeceraChat=cabecera,
                mensaje=user_input,
                idTipo='1',
                fechaMensaje=timezone.now()
            )

            # Maneja el flujo de conversación
            if conversation_state == 'waiting_for_client_status':
                if user_input.lower() in ['sí', 'si', 'yes', 'afirmativo']:
                    chatbot_reply = "Por favor, proporciona tu RUC o Cédula:"
                    request.session['conversation_state'] = 'waiting_for_code'
                else:
                    chatbot_reply = "Entiendo. ¿En qué más puedo ayudarte con respecto a Electrónica Siglo 21?"
                    request.session['conversation_state'] = 'general_conversation'
            elif conversation_state == 'waiting_for_code':
                codigo_cliente = user_input.strip()
                
                # Verificar si el cliente está registrado
                client_name = get_client_name(codigo_cliente)
                
                if client_name:
                    # Generar y guardar el código OTP
                    codigo_otp = generate_otp()
                    CodigoOTP.objects.create(
                        codigo_cliente=codigo_cliente,
                        codigo_otp=codigo_otp
                    )
                    
                    chatbot_reply = f"Se ha enviado un código OTP a tu correo electrónico. Por favor, ingresa el código de 4 dígitos que has recibido."
                    request.session['conversation_state'] = 'waiting_for_otp'
                    request.session['codigo_cliente'] = codigo_cliente
                    request.session['otp_attempts'] = 0  # Reiniciar el contador de intentos fallidos
                else:
                    chatbot_reply = "No estás registrado como cliente. Por favor, verifica tu RUC o Cédula y vuelve a intentarlo."
                    request.session['conversation_state'] = 'initial'  # Reinicia el estado de la conversación
            elif conversation_state == 'waiting_for_otp':
                user_otp = user_input.strip()
                codigo_cliente = request.session.get('codigo_cliente')
                
                # Verificar el código OTP
                try:
                    otp_record = CodigoOTP.objects.filter(
                        codigo_cliente=codigo_cliente,
                        codigo_otp=user_otp
                    ).latest('fecha_generacion')

                    # OTP verificado correctamente
                    client_name = get_client_name(codigo_cliente)
                    if client_name:
                        chatbot_reply = f"Código OTP verificado correctamente. Bienvenido, {client_name}. ¿En qué puedo ayudarte hoy?"
                    else:
                        chatbot_reply = f"Código OTP verificado correctamente, pero no pude encontrar tu nombre en nuestros registros. ¿En qué puedo ayudarte hoy?"

                    request.session['conversation_state'] = 'general_conversation'
                except CodigoOTP.DoesNotExist:
                    otp_attempts += 1
                    request.session['otp_attempts'] = otp_attempts

                    if otp_attempts >= 3:
                        chatbot_reply = "Código OTP incorrecto. Lo has intentado demasiadas veces. Inténtalo más tarde."
                        request.session['conversation_state'] = 'general_conversation'  # Cambiar a conversación general
                    else:
                        chatbot_reply = f"El código OTP ingresado no es válido. Te quedan {3 - otp_attempts} intentos."
            else:
                # Conversación general usando Gemini
                prompt = f"""Eres un asistente virtual para el siguiente negocio. 
                Información del negocio:
                {business_info}
                
                Instrucciones:
                1. Responde únicamente a preguntas relacionadas con la información proporcionada sobre el negocio.
                2. Si la pregunta no está relacionada con el negocio, responde cortésmente que solo puedes proporcionar información sobre el negocio.
                3. Sé conciso y directo en tus respuestas.
                4. Responde únicamente en español.
                5. No respondas con groserías ni con faltas de respeto
                Pregunta del cliente: {user_input}

                Respuesta:"""

                response = model.generate_content(prompt)
                chatbot_reply = response.text if response and response.text else "Lo siento, no pude generar una respuesta. Intenta otra pregunta."

            # Guarda la respuesta del chatbot
            DetalleChat.objects.create(
                idCabeceraChat=cabecera,
                mensaje=chatbot_reply,
                idTipo='0',
                fechaMensaje=timezone.now()
            )
            
            return JsonResponse({'reply': chatbot_reply, 'cabecera_id': cabecera_id})
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'error': f'Error al procesar la solicitud: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def chatbot_page(request):
    return render(request, 'chatbot.html')

def dashboard_page(request):
    return render(request, 'dashboard.html')
