import json
import requests
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name
from ask_sdk_core.handler_input import HandlerInput

class CaptureSpeechIntentHandler(AbstractRequestHandler):
    """Handler para capturar o que o usuário fala e enviar ao endpoint."""
    def can_handle(self, handler_input):
        # Verifica se o Intent é o CaptureSpeechIntent
        return is_intent_name("CaptureSpeechIntent")(handler_input)

    def handle(self, handler_input):
        # Captura o valor do slot 'speech'
        slots = handler_input.request_envelope.request.intent.slots
        speech = slots["speech"].value if "speech" in slots else None

        if speech:
            # Envia os dados para o endpoint
            endpoint_url = "https://api.example.com/endpoint"  # Substitua pelo seu endpoint
            payload = {"speech": speech}
            headers = {"Content-Type": "application/json"}

            try:
                response = requests.post(endpoint_url, json=payload, headers=headers)
                response_message = "Mensagem enviada com sucesso!" if response.status_code == 200 else \
                                   "Houve um problema ao enviar a mensagem."
            except Exception as e:
                print(f"Erro ao enviar dados para o endpoint: {e}")
                response_message = "Ocorreu um erro ao processar sua solicitação."
        else:
            response_message = "Não consegui entender o que você disse. Tente novamente."

        # Retorna uma resposta para o usuário
        return handler_input.response_builder.speak(response_message).get_response()

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler para quando a skill é iniciada."""
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "LaunchRequest"

    def handle(self, handler_input):
        speak_output = "Bem-vindo! Diga algo para que eu possa enviar para o endpoint."
        return handler_input.response_builder.speak(speak_output).get_response()

class HelpIntentHandler(AbstractRequestHandler):
    """Handler para o intent de ajuda."""
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "Você pode dizer qualquer coisa, e eu enviarei para o endpoint configurado."
        return handler_input.response_builder.speak(speak_output).get_response()

class CancelAndStopIntentHandler(AbstractRequestHandler):
    """Handler para intents de cancelamento ou parada."""
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.CancelIntent")(handler_input) or is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "Até mais!"
        return handler_input.response_builder.speak(speak_output).get_response()

# Inicializa o Skill Builder
sb = SkillBuilder()

# Adiciona os handlers à skill
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CaptureSpeechIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())

# Função Lambda
lambda_handler = sb.lambda_handler()
