import discord
from discord.ext import commands, tasks
import datetime, pytz, aiohttp, os

KSA = pytz.timezone('Asia/Riyadh')
times = {}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

# روابط ثابتة RadioJar - ما تعطي 404
KHUZAMA = "https://stream.radiojar.com/4wqre23um86uv"
NIDA = "https://stream.radiojar.com/8s5u5tpdtwzuv"

FFMPEG = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

async def update_times():
    global times
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("http://api.aladhan.com/v1/timingsByCity?city=Makkah&country=Saudi Arabia&method=4") as r:
                j = await r.json()
                times = j['data']['timings']
                print(f"Prayer times updated: {times}")
    except Exception as e:
        print(f"Prayer error: {e}")

def get_url():
    now = datetime.datetime.now(KSA)
    # الجمعة 11 - 2
    if now.weekday() == 4 and 11 <= now.hour < 14:
        return NIDA, "جمعة"
    # 25 دقيقة وقت كل صلاة
    for p in ["Fajr","Dhuhr","Asr","Maghrib","Isha"]:
        if p in times:
            try:
                hh, mm = map(int, times[p].split()[0].split(':'))
                pt = now.replace(hour=hh, minute=mm, second=0)
                if pt <= now < pt + datetime.timedelta(minutes=25):
                    return NIDA, p
            except: pass
    return KHUZAMA, "khuzama"

def play(vc, url):
    vc.current_url = url
    vc.play(discord.FFmpegPCMAudio(url, **FFMPEG))

@tasks.loop(minutes=1)
async def checker():
    for vc in bot.voice_clients:
        try:
            url, reason = get_url()
            if getattr(vc, 'current_url', None)!= url or not vc.is_playing():
                print(f"Switching to {reason}: {url}")
                try: vc.stop()
                except: pass
                play(vc, url)
        except Exception as e:
            print(f"Checker error: {e}")

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user} - KHUZAMA + NIDA AUTO")
    await update_times()
    checker.start()

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("ادخل روم صوتي")
        return
    ch = ctx.author.voice.channel
    vc = ctx.voice_client or await ch.connect()
    if ctx.guild.voice_client and vc.channel!= ch:
        await vc.move_to(ch)

    url, reason = get_url()
    if vc.is_playing(): vc.stop()
    play(vc, url)

    if url == NIDA:
        await ctx.send(f"✅ شغال: نداء الإسلام 🕋 (سبب: {reason})")
    else:
        await ctx.send("✅ شغال: خزامى طرب 24 ساعة 🎵")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(os.getenv("DISCORD_TOKEN"))
