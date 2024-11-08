import asyncio
import discord
import os
import uvicorn
from discord.ext import commands
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fuzzywuzzy import fuzz

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True
bot = commands.Bot(command_prefix='.', intents=intents)

app = FastAPI()
config = uvicorn.Config(app, host="0.0.0.0", port=8000)
server = uvicorn.Server(config)

@bot.event
async def on_ready():
    print(f'Aplicação conectada como {bot.user}.')

def get_status():
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
    return status

def get_user_id_by_nick(status, nick):
    for user_id, user_info in status.items():
        if user_info["display_name"] == nick:
            return int(user_id)
    return None

def get_guild_id_by_nick(status, nick):
    for user_info in status.values():
        if user_info["display_name"] == nick:
            return int(user_info["guild_id"])
    return None

def fuzzy_analysis(status, heard_nickname):
    online_nicknames = [user_info["display_name"] for user_info in status.values()]
    matches = [(nome, fuzz.ratio(heard_nickname, nome.lower())) for nome in online_nicknames]
    filtered_matches = [match for match in matches if match[1] >= 65]
    return filtered_matches

async def disconnect_user(guild_id: int, member_id: int):
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

async def move_user(guild_id: int, member_id: int, target_channel_id: int):
    guild = bot.get_guild(guild_id)
    if guild:
        member = guild.get_member(member_id)
        if member:
            if member.voice:
                past_voice_channel = member.voice.channel.name
                target_channel = guild.get_channel(target_channel_id)
                if target_channel:
                    await member.move_to(target_channel)
                    return f'{member.display_name} foi movido de {past_voice_channel} para {member.voice.channel.name} em {guild.name}.'
                else:
                    return f'Canal de voz {target_channel_id} não encontrado.'
            else:
                return f'{member.display_name} não está em um canal de voz no momento.'
        else:
            return f'Membro {member_id} não encontrado no servidor {guild.name}.'
    else:
        return f'Servidor {guild_id} não encontrado.'

@app.post("/disconnect_user/")
async def disconnect_user_endpoint(request: Request):
    try:
        data = await request.json()
        print(str(data))
        if data['request']['type'] == 'LaunchRequest':
            response = 'Qual o comando a ser executado?'
        elif data['request']['type'] == 'IntentRequest':
            status = get_status()
            print('Status: ',str(status))
            nickname = data['request']['intent']['slots']['NomeUsuario']['slotValue']['value']
            print('Nick informado pela Alexa: ', str(nickname))
            filtered_nicks = fuzzy_analysis(status, nickname)
            print('Nicks filtrados: ', filtered_nicks)
            server_id = get_guild_id_by_nick(status, filtered_nicks[0][0])
            member_id = get_user_id_by_nick(status, filtered_nicks[0][0])
            response = await disconnect_user(server_id, member_id)
        else:
            response = 'Intent não identificado'

        return JSONResponse(content={
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": response
                },
                "shouldEndSession": False
            }
        })
    
    except Exception as e:
        print("Erro ao processar a requisição:", str(e))
        return JSONResponse(status_code=422, content={"message": "Erro ao processar a requisição"})

async def main():
    await asyncio.gather(bot.start(BOT_TOKEN), server.serve())

if __name__ == "__main__":
    asyncio.run(main())