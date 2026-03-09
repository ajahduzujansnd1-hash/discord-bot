import discord
from discord.ext import commands
import os
import replicate

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

last_image = None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# TEXT → IMAGE
@bot.command()
async def imagine(ctx, *, prompt):
    global last_image
    await ctx.send("Generating image... 🎨")

    output = replicate.run(
        "stability-ai/sdxl",
        input={"prompt": prompt}
    )

    last_image = output[0]
    await ctx.send(output[0])


# IMAGE → EDIT
@bot.command()
async def edit(ctx, *, prompt):
    global last_image

    if len(ctx.message.attachments) == 0:
        await ctx.send("Attach an image to edit.")
        return

    img = ctx.message.attachments[0].url

    await ctx.send("Editing image... ✏️")

    output = replicate.run(
        "stability-ai/sdxl",
        input={
            "image": img,
            "prompt": prompt
        }
    )

    last_image = output[0]
    await ctx.send(output[0])


# REMIX TWO IMAGES
@bot.command()
async def remix(ctx, *, prompt="combine these images"):
    global last_image

    if len(ctx.message.attachments) < 2:
        await ctx.send("Attach 2 images.")
        return

    img1 = ctx.message.attachments[0].url
    img2 = ctx.message.attachments[1].url

    await ctx.send("Mixing images... 🎨")

    output = replicate.run(
        "stability-ai/sdxl",
        input={
            "image": img1,
            "prompt": f"{prompt} inspired by this style {img2}"
        }
    )

    last_image = output[0]
    await ctx.send(output[0])


# EDIT LAST IMAGE AGAIN
@bot.command()
async def redo(ctx, *, prompt):
    global last_image

    if last_image is None:
        await ctx.send("No previous image to edit.")
        return

    await ctx.send("Editing last image... 🔄")

    output = replicate.run(
        "stability-ai/sdxl",
        input={
            "image": last_image,
            "prompt": prompt
        }
    )

    last_image = output[0]
    await ctx.send(output[0])


bot.run(os.getenv("TOKEN"))
