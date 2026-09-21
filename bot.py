import discord
from discord.ext import commands
import os
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

NIDA = "https://stream.radiojar.com/8s5u5tpdtwzuv"
# رابط خزامى الجديد - RadioJar ثابت ما ينتهي مثل Zeno
KHUZAMA = "https://stream.radiojar.com/4wqre23um86uv"

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user}")

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("ادخل روم")
        return
    vc = ctx.voice_client or await ctx.author.voice.channel.connect()
    # جرب خزامى اول
    try:
        vc.play(discord.FFmpegPCMAudio(KHUZAMA, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn'))
        await ctx.send("✅ شغال: خزامى 🎵")
    except Exception as e:
        # اذا خزامى ما اشتغل شغل قرآن
        vc.play(discord.FFmpegPCMAudio(NIDA, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn'))
        await ctx.send(f"خزامى مو شغال حاليا شغلت قرآن: {e}")

@bot.command()
async def khuzama(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        ctx.voice_client.play(discord.FFmpegPCMAudio(KHUZAMA, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn'))
        await ctx.send("✅ خزامى")

@bot.command()
async def nida(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        ctx.voice_client.play(discord.FFmpegPCMAudio(NIDA, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn'))
        await ctx.send("✅ نداء الإسلام")

@bot.command()
async def leave(ctx):
    if ctx.voice_client: await ctx.voice_client.disconnect()

bot.run(os.getenv("DISCORD_TOKEN"))
