import discord
from discord.ext import commands
import os
import replicate

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def remix(ctx, *, prompt="mix these images"):
    if len(ctx.message.attachments) < 2:
        await ctx.send("Attach 2 images with the command.")
        return

    img1 = ctx.message.attachments[0].url
    img2 = ctx.message.attachments[1].url

    await ctx.send("Generating AI remix... 🎨")

    try:
        output = replicate.run(
            "stability-ai/sdxl",
            input={
                "image": img1,
                "prompt": f"{prompt}, inspired by the style of this second image: {img2}"
            }
        )

        await ctx.send(output[0])

    except Exception as e:
        await ctx.send(f"Error: {e}")

bot.run(os.getenv("TOKEN"))
