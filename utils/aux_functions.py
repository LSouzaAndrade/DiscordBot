from fastapi import Request
from fastapi.responses import JSONResponse
from utils.discord_functions import *

async def command_parser(request: Request):
    try:
        data = await request.json()
        match data['request']['type']:
            case 'LaunchRequest':
                response = 'Assistente de servidor iniciado.'
                shouldEndSession = False
            case 'IntentRequest':
                match data['request']['intent']['name']:
                    case 'MoveUserIntent':
                        ...
                    case 'MuteUserIntent':
                        ...
                    case 'KickUserIntent':
                        response = kick_user(data['request']['intent']['name'])
                        shouldEndSession = False
                    case 'AMAZON.HelpIntent':
                        response = 'O assistente de servidor pode expulsar, mover e silenciar usuários. Além de tocar música.'
                        shouldEndSession = False
                    case 'AMAZON.StopIntent' | 'AMAZON.CancelIntent' | 'AMAZON.NavigateHomeIntent':
                        response = 'Assistente de servidor finalizado.'
                        shouldEndSession = True
            case 'SessionEndedRequest':
                response = 'Assistente de servidor finalizado.'
                shouldEndSession = True
            case 'System.ExceptionRequest' | _:
                response = 'Erro ao processar comando. Finalizando assistente de servidor.'
                shouldEndSession = True

        return JSONResponse(content={
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": response
                },
                "shouldEndSession": shouldEndSession
            }
        })

    except Exception as e:
        print("Erro ao processar a requisição:", str(e))
        return JSONResponse(status_code=422, content={"message": "Erro ao processar a requisição"})