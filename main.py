import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import json
from db_manager import initialize_database, add_or_update_user, get_user_points
from scheduler import reset_monthly
from utils import update_user_roles, reward_user

# Cargar configuración desde config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Configurar intents y prefijo
intents = discord.Intents.default()
intents.messages = True
intents.voice_states = True
intents.guilds = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Inicializar base de datos SQLite
initialize_database()

# Scheduler para tareas automáticas
scheduler = AsyncIOScheduler()

# Evento: Cuando el bot está listo
@bot.event
async def on_ready():
    await bot.tree.sync()  # Sincronizar comandos slash
    print(f'Bot conectado como {bot.user}')
    scheduler.start()

# Evento: Mensajes recibidos
@bot.event
async def on_message(message):
    if message.author.bot:  # Ignorar bots
        return

    # Actualizar puntos por mensaje enviado
    points_per_message = config["points"]["per_message"]
    user = add_or_update_user(message.author.id, messages=1, points=points_per_message)

    # Registrar actividad y actualizar roles
    await update_user_roles(message.guild, message.author, user["points"], config)

    # Recompensas
    notify_channel = bot.get_channel(config["notify_channel"])
    await reward_user(message.author, user["points"], config, notify_channel)

    await bot.process_commands(message)

# Evento: Actualización en canales de voz
@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:  # Ignorar bots
        return

    from datetime import datetime
    now = datetime.utcnow()

    # Si el usuario entra a un canal de voz
    if after.channel and not before.channel:
        add_or_update_user(member.id, vc_join_time=now.isoformat())

    # Si el usuario sale de un canal de voz
    elif before.channel and not after.channel:
        user = get_user_points(member.id)
        if user and user["vc_join_time"]:
            join_time = datetime.fromisoformat(user["vc_join_time"])
            time_spent = (now - join_time).total_seconds() / 60
            points_per_minute = config["points"]["per_minute"]

            new_points = user["points"] + (time_spent * points_per_minute)
            add_or_update_user(
                member.id,
                vc_join_time=None,
                voice_time=user["voice_time"] + time_spent,
                points=new_points,
            )

            # Registrar actividad y actualizar roles
            await update_user_roles(member.guild, member, new_points, config)

# Programar reseteo mensual
scheduler.add_job(lambda: reset_monthly(bot, config["guild_id"], config), 'cron', day=1, hour=0)

# Iniciar el bot
bot.run(config["token"])
