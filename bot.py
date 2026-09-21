import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

QURAN = "https://stream.radiojar.com/8s5u5tpdtwzuv"

@bot.event
async def on_ready():
    print(f"✅ Bot is ready! {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 {round(bot.latency*1000)}ms - شغال في Jeddah ✅")

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        return await ctx.send("❌ ادخل روم صوتي أول!")
    ch = ctx.author.voice.channel
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if vc:
        await vc.move_to(ch)
    else:
        vc = await ch.connect()
    if not vc.is_playing():
        vc.play(discord.FFmpegPCMAudio(QURAN))
    await ctx.send(f"✅ دخلت {ch.name}")

@bot.command()
async def quran(ctx):
    await join(ctx)

@bot.command()
async def leave(ctx):
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if vc:
        await vc.disconnect()
        await ctx.send("👋 طلعت")

bot.run(os.getenv("TOKEN"))
