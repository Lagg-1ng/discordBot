import json
import discord
from discord import Intents
from config import settings
import sqlite3
import threading

# Переменные для работы с базой данных
conn = sqlite3.connect('events.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        event_name TEXT
    )
''')
conn.commit()

# Переменные для игры в города
cities_already_named = set()

# Добавим database_lock здесь
database_lock = threading.Lock()

def add_event(date, event_name):
    cursor.execute('INSERT INTO events (date, event_name) VALUES (?, ?)', (date, event_name))
    conn.commit()

# Остальной код без изменений

intents = Intents.default()
intents.message_content = True  # Необходимые вам интенты

TOKEN = settings['token']

bot = discord.Client(intents=intents)

@bot.event
async def on_message(message):
    global cities_already_named

    # Преобразуем команду в нижний регистр
    command = message.content.lower()

    # Проверяем, что автор не бот
    if message.author == bot.user:
        return

    # Проверяем, начинается ли сообщение с '!'
    if command.startswith('!'):
        # Обработка команды !refresh
        if command == '!refresh':
            refresh()
            await message.channel.send('Список городов обновлен.')
        # Обработка команды !help или !помощь
        elif command == '!help' or command == '!помощь':
            await message.channel.send('Помощи не будет, я умею только в города')
        # Обработка команды !хуй
        elif command == '!хуй':
            await message.channel.send('Ха-ха долго придумывал?')
        # Обработка команды !запиши событие
        elif command.startswith('!запиши событие'):
            await message.channel.send('Чтобы записать событие, укажите дату и название события в формате: !запиши событие дата название')

            # Ожидание сообщения с данными о событии
            def check(msg):
                return msg.author == message.author and msg.channel == message.channel

            response = await bot.wait_for('message', check=check)

            # Обработка и сохранение события
            date, event_name = response.content.split()[2], ' '.join(response.content.split()[3:])

            # Заблокировать доступ к базе данных
            with database_lock:
                add_event(date, event_name)
                await message.channel.send('Событие успешно записано')

@bot.event
async def on_disconnect():
    conn.close()

bot.run(TOKEN)
