import discord, re, aiohttp, datetime, pytz
from discord.ext import commands, tasks
import os

KSA = pytz.timezone('Asia/Riyadh')
times = {}
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

QURAN = "https://stream.radiojar.com/8s5u5tpdtwzuv"
OFFICIAL_PAGE = "https://radioplus.sba.sa/live/7"

FFMPEG_OPTS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -user_agent "Mozilla/5.0"',
    'options': '-vn'
}

async def get_live_hls():
    # نسحب رابط m3u8 الحقيقي من صفحتك
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(OFFICIAL_PAGE, headers={"User-Agent":"Mozilla/5.0"}, timeout=20) as r:
                html = await r.text()
                # دور على اي رابط m3u8
                matches = re.findall(r'https://[^"\']+\.m3u8[^"\']*', html)
                for m in matches:
                    clean = m.replace('\\u002F','/').replace('\\','').replace('\\/','/')
                    if 'khuzama' in clean.lower() or 'sba' in clean.lower() or 'live' in clean.lower():
                        print(f"Found HLS: {clean}")
                        return clean
                if matches:
                    return matches[0].replace('\\u002F','/').replace('\\','')
    except Exception as e:
        print(f"Extract error: {e}")
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
    if now.weekday()==4 and 11 <= now.hour < 14:
        return True
    for p in ["Fajr","Dhuhr","Asr","Maghrib","Isha"]:
        if p in times:
            try:
                hh,mm = map(int, times[p].split()[0].split(':'))
                pt = now.replace(hour=hh, minute=mm, second=0)
                if pt <= now < pt + datetime.timedelta(minutes=25):
                    return True
            except: pass
    return False

@tasks.loop(minutes=2)
async def checker():
    for vc in bot.voice_clients:
        try:
            target_is_quran = is_prayer()
            if target_is_quran:
                url = QURAN
            else:
                hls = await get_live_hls()
                url = hls if hls else QURAN

            if getattr(vc, 'current_url', None)!= url or not vc.is_playing():
                try: vc.stop()
                except: pass
                vc.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTS))
                vc.current_url = url
        except Exception as e:
            print(f"Checker error: {e}")

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user}")
    await update_times()
    checker.start()

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("ادخل روم صوتي")
        return
    vc = ctx.voice_client or await ctx.author.voice.channel.connect()
    if ctx.guild.voice_client and vc.channel!= ctx.author.voice.channel:
        await vc.move_to(ctx.author.voice.channel)
    if vc.is_playing():
        vc.stop()

    url = QURAN if is_prayer() else await get_live_hls()
    if not url:
        await ctx.send("❌ ما قدرت اسحب بث خزامى (SBA حاظر امريكا)، شغلت قرآن مؤقتاً")
        url = QURAN

    try:
        # بدون from_probe عشان ما يعطي الخطأ اللي في صورتك
        vc.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTS))
        vc.current_url = url
        if url == QURAN:
            await ctx.send("✅ شغال: نداء الإسلام 🕋 (خزامى محجوب من سيرفر امريكا)")
        else:
            await ctx.send("✅ شغال: خزامى طرب 24 ساعة 🎵 - من رابطك الرسمي")
    except Exception as e:
        await ctx.send(f"خطأ: {e}")
        print(e)

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(os.getenv("DISCORD_TOKEN"))
