import discord
from googletrans import Translator
import FuncionesBusqueda as FB
import FuncionesCombate as FC
import FuncionesDados as FD
import FuncionesDEV as DEV
import FuncionesAvanzadas as FA
import os

from dotenv import load_dotenv
load_dotenv()
global EstadoDelBot 
EstadoDelBot = True
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("DISCORD_TOKEN no está definido en el archivo .env")
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True        
intents.presences = False 
client = discord.Client(intents=intents)


translator = Translator()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    MSJCTT = message.content.strip().lower()

    #Developer Commands
    if message.author.id == 743531557863817237:
        if MSJCTT == "j!dev apagate":
            await message.channel.send("Okay... me voy a apagar jefe... Adios!")
            global EstadoDelBot 
            EstadoDelBot = False
        if MSJCTT == "j!dev enciendete":
            await message.channel.send("Ya estoy de vuelta jefe!")
            EstadoDelBot = True
        if MSJCTT == "j!dev list":
            await DEV.listar_combates_para_dev(message.author)
        if MSJCTT == "j!dev wipe":
            await DEV.borrar_todos_los_combates(message.author)
        if MSJCTT == "j!dev fresh":
            await DEV.borrar_combates_viejos(message.author)
        if MSJCTT.startswith("j!dev kill "):
            nombre = MSJCTT[10:].strip()
            await DEV.borrar_combate_por_nombre(message.author, nombre)

    if EstadoDelBot:
        #Basic Commands
        if message.content.lower().startswith('j!como puedes ayudarme?'):
            await message.channel.send(await FB.comandos())
        if message.content.lower().startswith('j!lanzame'):
            await message.channel.send(await FD.lanzar_dados(message.content))
        if message.content.lower().startswith('j!explicame'):
            await message.channel.send(await FB.BusquedaCondicion(message))
        if message.content.lower() == 'josefina!':
            await message.channel.send(f'hola {message.author.mention}! soy Josefina, tu asistente de dnd!')
        if message.content.startswith("j!genera estadisticas"):
            await FD.comando_generar_estadisticas(message)
        #Combat Commands
        if MSJCTT.startswith("j!inicia un combate llamado"):
            await FC.iniciar_combate(message, client)
        elif await FC.registrar_iniciativa(message):
            pass
        elif MSJCTT.startswith("j!mostrar iniciativa de"):
            await FC.mostrar_iniciativa(message)
        #interaction commands
        if MSJCTT == 'j!buenas noches':
            await message.channel.send(f'bay! duerme bien {message.author.mention} <3')
        #advanced commands
        if MSJCTT == ("j!roll"):
            await message.channel.send("Porfa probá con algo como:\n 'j!roll 2d6+1d4+3 adv x4'")
        elif MSJCTT.startswith("j!roll "):
            await FA.comando_roll_profesional(message)
client.run(TOKEN)
