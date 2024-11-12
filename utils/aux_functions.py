

def get_online_users():
    status = {}
    for guild in bot.guilds:
        for channel in guild.voice_channels:
            for member in channel.members:
                member_info = {
                    "display_name": member.display_name,
                    "voice_channel_id": str(channel.id),
                    "guild_id": str(guild.id)
                }
                status[str(member.id)] = member_info
    print ("Status: ", status)
    return status

def get_user_id(status, nickname):
    for user_id, user_info in status.items():
        if user_info["display_name"] == nickname:
            return int(user_id)
    return None

def get_guild_id(status, nickname):
    for user_info in status.values():
        if user_info["display_name"] == nickname:
            return int(user_info["guild_id"])
    return None

def fuzzy_analysis(status, heard_nickname):
    online_nicknames = [user_info["display_name"] for user_info in status.values()]
    matches = [(nome, fuzz.ratio(heard_nickname, nome.lower())) for nome in online_nicknames]
    filtered_matches = [match for match in matches if match[1] >= 65]
    print("Filtered matches: ", filtered_matches)
    return filtered_matches

async def kick_user(nickname: str):
    status = get_online_users()
    nickname = fuzzy_analysis(status, nickname)[0][0]
    guild_id = get_guild_id(status, nickname)
    member_id = get_user_id(status, nickname)
    print("Kick Infos:", nickname, guild_id, member_id)
    guild = bot.get_guild(guild_id)
    if guild:
        member = guild.get_member(member_id)
        if member:
            if member.voice:
                voice_channel = member.voice.channel.name
                await member.move_to(None)
                return f'{member.display_name} foi expulso de {voice_channel} em {guild.name}.'
            else:
                return f'{member.display_name} não está em um canal de voz no momento.'
        else:
            return f'Membro {member_id} não encontrado no servidor {guild.name}.'
    else:
        return f'Servidor {guild_id} não encontrado.'

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
                        response = await kick_user(data['request']['intent']['slots']['NomeUsuario']['value'])
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