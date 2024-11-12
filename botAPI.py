import asyncio
import discord
import os
import uvicorn
from discord.ext import commands
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from utils.aux_functions import command_parser

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

@app.post("/")
async def command_parser_endpoint(request: Request):
    return await command_parser(request)

@bot.event
async def on_ready():
    print(f'Aplicação conectada como {bot.user}.')

async def main():
    await asyncio.gather(bot.start(BOT_TOKEN), server.serve())

if __name__ == "__main__":
    asyncio.run(main())