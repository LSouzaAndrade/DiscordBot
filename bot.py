import discord
from discord.ext import commands
from dotenv import load_dotenv
import os


load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)


@bot.event
async def on_ready():
    print(f'Aplicação conectada como {bot.user}.')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        message = await ctx.send("Esse comando não existe.", delete_after=3)


@bot.command()
async def oi(ctx:commands.Context):
    await ctx.reply(f'Oi, {ctx.author.display_name}!')


@bot.command()
async def limpar(ctx:commands.Context, amount:int=100):
    if isinstance(ctx.channel, discord.TextChannel):
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f'{len(deleted)} mensagem(s) deletada(s).', delete_after=3)
    else:
        await ctx.send("Este comando só pode ser utilizado em servidores.", delete_after=3)


bot.run(TOKEN)