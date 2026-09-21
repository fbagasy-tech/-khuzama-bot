import discord
from discord.ext import commands, tasks
import datetime
import pytz
import aiohttp
import os
import asyncio

# الروابط
KHUZAMI_URL = "https://stream-159.zeno.fm/6cuzb8f5xg8uv"
NIDA_URL = "https://stream.radiojar.com/8s5u5tpdtwzuv"

KSA = pytz.timezone('Asia/Riyadh')
prayer_times = {}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def update_prayers():
    global prayer_times
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("http://api.aladhan.com/v1/timingsByCity?city=Makkah&country=Saudi Arabia&method=4") as r:
                j = await r.json()
                prayer_times = j['data']['timings']
                print(prayer_times)
    except Exception as e:
        print(e)

def get_url():
    now = datetime.datetime.now(KSA)
    # الجمعة من 11 الى 2
    if now.weekday() == 4 and 11 <= now.hour < 14:
        return NIDA_URL
    # وقت الصلاة 25 دقيقة
    for p in ["Fajr","Dhuhr","Asr","Maghrib","Isha"]:
        if p in prayer_times:
            try:
                hh, mm = map(int, prayer_times[p].split()[0].split(':'))
                pt = now.replace(hour=hh, minute=mm, second=0)
                if pt <= now < pt + datetime.timedelta(minutes=25):
                    return NIDA_URL
            except: pass
    return KHUZAMI_URL

@tasks.loop(minutes=1)
async def checker():
    for vc in bot.voice_clients:
        url = get_url()
        if getattr(vc, 'current_url', None)!= url:
            vc.stop()
            vc.current_url = url
            vc.play(discord.FFmpegPCMAudio(url))

@bot.event
async def on_ready():
    print(f"Ready {bot.user}")
    await update_prayers()
    checker.start()

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("ادخل روم صوتي اول")
        return
    vc = ctx.voice_client or await ctx.author.voice.channel.connect()
    if ctx.voice_client and ctx.voice_client.channel!= ctx.author.voice.channel:
        await vc.move_to(ctx.author.voice.channel)
    url = get_url()
    vc.current_url = url
    vc.play(discord.FFmpegPCMAudio(url))
    await ctx.send(f"شغال: {'نداء الاسلام - مكة' if url==NIDA_URL else 'خزامى'}")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@bot.command()
async def ping(ctx):
    await ctx.send("شغال")

bot.run(os.getenv("DISCORD_TOKEN"))
