import os
import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# رابط الراديو - ياخذه من Railway Variables او يستخدم البروكسي حقك
RADIO_URL = os.getenv("RADIO_URL") or os.getenv("STREAM_URL") or "https://spring-butterfly-de76.fbagasy.workers.dev/?stream=https%3A%2F%2Fsba-radio-live1.sba.gov.sa%3A8443%2FkhuzamaRadio%2FkhuzamaRadio.m3u8"

# اعدادات FFMPEG تخلي البث يشتغل مع m3u8
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f"Bot ready: {bot.user}")

@bot.command(name="join")
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("❌ لازم تدخل روم صوتي أول!")
        return
    
    channel = ctx.author.voice.channel
    
    try:
        if ctx.voice_client is None:
            vc = await channel.connect()
        else:
            vc = ctx.voice_client
            if vc.channel != channel:
                await vc.move_to(channel)
        
        # اذا كان شغال شي وقفه
        if vc.is_playing():
            vc.stop()
        
        print(f"Playing URL: {RADIO_URL}")
        source = discord.FFmpegPCMAudio(RADIO_URL, **FFMPEG_OPTIONS)
        vc.play(source, after=lambda e: print(f"Player ended: {e}"))
        await ctx.send(f"✅ شغلت إذاعة خزامى في {channel.name} 📻")
        
    except Exception as e:
        print(f"Error in join: {e}")
        await ctx.send(f"❌ صار خطأ: {e}")
        import traceback
        traceback.print_exc()

@bot.command(name="leave")
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 طلعت من الروم")
    else:
        await ctx.send("انا مو في روم اصلاً")

@bot.command(name="stop")
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹️ وقفت البث")

bot.run(os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN"))
