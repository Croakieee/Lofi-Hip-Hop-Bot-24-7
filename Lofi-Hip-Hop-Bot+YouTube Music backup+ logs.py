import nextcord
import asyncio
from nextcord.ext import commands
import yt_dlp

intents = nextcord.Intents.all()
intents.voice_states = True
intents.guilds = True
intents.messages = True
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
default_youtube_stream_url = "https://www.youtube.com/watch?v=rUxyKA_-grg&ab_channel=LofiGirl"

async def delete_message_after_delay(message, delay=30):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except nextcord.NotFound:
        pass

@bot.event
async def on_ready():
    print('AIM: Привет, Никколо! Готов выполнить любую твою команду.')

@bot.command()
async def join(ctx):
    await ctx.message.delete()
    channel = ctx.author.voice.channel
    if not ctx.voice_client:
        await channel.connect()
        reply = await ctx.send("AIM: Подключился к голосовому каналу.")
    else:
        reply = await ctx.send("AIM: Я уже подключён к голосовому каналу.")
    await delete_message_after_delay(reply)

@bot.command()
async def play_radio(ctx):
    await ctx.message.delete()
    voice_channel = nextcord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_channel:
        reply = await ctx.send("AIM: Я не подключён к голосовому каналу. Используйте `!join`, чтобы подключиться.")
        await delete_message_after_delay(reply)
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': 'song.mp3',
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(default_youtube_stream_url, download=False)
            if 'formats' in info:
                audio_url = next((f['url'] for f in info['formats'] if f.get('acodec') != 'none'), None)
                if not audio_url:
                    audio_url = info['formats'][0]['url']
            else:
                audio_url = info['url']
            voice_channel.stop()
            voice_channel.play(nextcord.FFmpegPCMAudio(audio_url), after=lambda e: print('Done', e))
        reply = await ctx.send("AIM: Воспроизведение радио началось.")
    except Exception as e:
        reply = await ctx.send(f"AIM: Возникла ошибка при воспроизведении радио - {str(e)}")

    await delete_message_after_delay(reply)

@bot.command()
async def play_other(ctx, *, url):
    await ctx.message.delete()
    voice_channel = nextcord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_channel:
        reply = await ctx.send("AIM: Я не подключён к голосовому каналу. Используйте `!join`, чтобы подключиться.")
        await delete_message_after_delay(reply)
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': 'song.mp3',
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'formats' in info:
                audio_url = next((f['url'] for f in info['formats'] if f.get('acodec') != 'none'), None)
                if not audio_url:
                    audio_url = info['formats'][0]['url']
            else:
                audio_url = info['url']
            voice_channel.stop()
            voice_channel.play(nextcord.FFmpegPCMAudio(audio_url), after=lambda e: print('Done', e))
        reply = await ctx.send("AIM: Воспроизведение видео началось.")
    except Exception as e:
        reply = await ctx.send(f"AIM: Возникла ошибка при воспроизведении - {str(e)}")

    await delete_message_after_delay(reply)

@bot.command()
async def stop(ctx):
    await ctx.message.delete()
    voice_channel = nextcord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_channel:
        reply = await ctx.send("AIM: Я не подключён к голосовому каналу.")
        await delete_message_after_delay(reply)
        return

    if not voice_channel.is_playing():
        reply = await ctx.send("AIM: В данный момент ничего не воспроизводится.")
        await delete_message_after_delay(reply)
        return

    voice_channel.stop()
    reply = await ctx.send("AIM: Воспроизведение остановлено.")
    await delete_message_after_delay(reply)

@bot.command()
async def thx(ctx):
    await ctx.message.delete()
    reply = await ctx.send("Спасибо за поддержку!!!")
    await delete_message_after_delay(reply)

@bot.command()
async def h(ctx):
    await ctx.message.delete()
    help_message = """
    **AIM: Список доступных команд и инструкция**
    
    **!join** — подключает бота к голосовому каналу, в котором находится пользователь.
    Пример: `!join`

    **!play_radio** — начинает воспроизведение заранее заданного радио.
    Пример: `!play_radio`

    **!play_other <ссылка>** — начинает воспроизведение по предоставленной YouTube ссылке.
    Пример: `!play_other https://www.youtube.com/watch?v=dQw4w9WgXcQ`

    **!stop** — останавливает текущее воспроизведение.
    Пример: `!stop`

    **!thx** — благодарность от бота. Показывает сообщение благодарности в чате.
    Пример: `!thx`

    **!del_messages <количество>** — удаляет указанное количество сообщений. 
    Пример: `!del_messages 50`

    **!h** — показывает это сообщение с инструкциями.
    Пример: `!h`

    *Для работы команд убедитесь, что бот имеет необходимые разрешения на сервере.*
    """
    message = await ctx.send(help_message)
    await delete_message_after_delay(message)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def del_messages(ctx, amount: int):
    if amount < 1 or amount > 100:
        reply = await ctx.send("AIM: Введите количество сообщений от 1 до 100.")
        await delete_message_after_delay(reply)
        return

    # Удаляем команду сама по себе, добавив 1 к количеству
    deleted = await ctx.channel.purge(limit=amount + 1)
    reply = await ctx.send(f"AIM: Удалено {len(deleted) - 1} сообщений.")  # -1 потому что команда сама удаляется
    await delete_message_after_delay(reply)

# Обработчик ошибок
@bot.event
async def on_command_error(ctx, error):
    await ctx.message.delete()
    if isinstance(error, commands.CommandNotFound):
        error_message = "AIM: Эта команда не существует. Пожалуйста, проверьте правильность команды или используйте `!h`, чтобы увидеть список доступных команд."
    else:
        error_message = f"AIM: Произошла ошибка: {str(error)}. Попробуйте ещё раз или проверьте правильность команды с помощью `!h`."

    message = await ctx.send(error_message)
    await delete_message_after_delay(message)

@bot.event
async def on_error(event, *args, **kwargs):
    error_message = f"AIM: Произошла ошибка: {str(args[0])}. Попробуйте ещё раз или обратитесь к администратору."
    for channel in bot.get_all_channels():
        if isinstance(channel, nextcord.TextChannel):
            await channel.send(error_message)

bot.run('YOUR_BOT_TOKEN')  # Замените YOUR_BOT_TOKEN на токен вашего бота


