import discord
from discord.ext import commands
import os

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
async def remix(ctx):
    if len(ctx.message.attachments) < 2:
        await ctx.send("Send 2 images with the command.")
        return

    img1 = ctx.message.attachments[0].url
    img2 = ctx.message.attachments[1].url

    print("Image 1:", img1)
    print("Image 2:", img2)

    await ctx.send("Mixing images... 🎨")

bot.run(os.getenv("TOKEN"))
