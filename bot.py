import asyncio
import discord
import os
import uvicorn
from discord.ext import commands
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

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

class ActionRequest(BaseModel):
    guild_id: int
    member_id: int
    target_channel_id: int = None

@bot.event
async def on_ready():
    print(f'Aplicação conectada como {bot.user}.')

def get_status():
    status = {}
    for guild in bot.guilds:
        guild_info = {
            "nome_servidor": guild.name,
            "canais_de_voz": {}
        }
        for channel in guild.voice_channels:
            channel_info = {
                "nome_canal": channel.name,
                "membros_conectados": {}
            }
            for member in channel.members:
                channel_info["membros_conectados"][str(member.id)] = member.display_name

            guild_info["canais_de_voz"][str(channel.id)] = channel_info
        status[str(guild.id)] = guild_info
    print(str(status))

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
async def disconnect_user_endpoint(action: ActionRequest):
    response = await disconnect_user(action.guild_id, action.member_id)
    return {"message": response}

@app.post("/move_user/")
async def move_user_endpoint(action: ActionRequest):
    if action.target_channel_id:
        response = await move_user(action.guild_id, action.member_id, action.target_channel_id)
        return {"message": response}
    else:
        return {"error": "É necessário fornecer o ID do canal de destino"}


async def main():
    await asyncio.gather(bot.start(BOT_TOKEN), server.serve())

if __name__ == "__main__":
    asyncio.run(main())