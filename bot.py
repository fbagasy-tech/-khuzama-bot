import discord, re, aiohttp, datetime, pytz, os
from discord.ext import commands, tasks

KSA = pytz.timezone('Asia/Riyadh')
times = {}
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

QURAN = "https://stream.radiojar.com/8s5u5tpdtwzuv"
PAGE = "https://radioplus.sba.sa/live/7"
FFMPEG = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -user_agent "Mozilla/5.0"', 'options': '-vn'}

async def get_hls():
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(PAGE, headers={"User-Agent":"Mozilla/5.0"}, timeout=20) as r:
                html = await r.text()
                m = re.findall(r'https://[^"\']+\.m3u8[^"\']*', html)
                if m:
                    return m[0].replace('\\u002F','/').replace('\\','')
    except Exception as e:
        print(e)
    return None

async def update_times():
    global times
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("http://api.aladhan.com/v1/timingsByCity?city=Makkah&country=Saudi Arabia&method=4") as r:
                j = await r.json()
                times = j['data']['timings']
    except: pass

def is_prayer():
    now = datetime.datetime.now(KSA)
    if now.weekday()==4 and 11 <= now.hour < 14: return True
    for p in ["Fajr","Dhuhr","Asr","Maghrib","Isha"]:
        if p in times:
            try:
                hh,mm = map(int, times[p].split()[0].split(':'))
                pt = now.replace(hour=hh, minute=mm)
                if pt <= now < pt + datetime.timedelta(minutes=25): return True
            except: pass
    return False

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency*1000)}ms")

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("ادخل روم صوتي")
        return
    vc = ctx.voice_client
    if not vc:
        vc = await ctx.author.voice.channel.connect()
    else:
        if vc.channel!= ctx.author.voice.channel:
            await vc.move_to(ctx.author.voice.channel)
    if vc.is_playing(): vc.stop()

    url = QURAN if is_prayer() else await get_hls()
    if not url: url = QURAN

    vc.play(discord.FFmpegPCMAudio(url, **FFMPEG))
    vc.current_url = url
    await ctx.send("✅ شغال: " + ("نداء الإسلام 🕋" if url==QURAN and is_prayer() else "خزامى 🎵"))

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("طلعت")

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user}")
    await update_times()

bot.run(os.getenv("DISCORD_TOKEN"))
