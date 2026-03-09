import discord
from discord.ext import commands
import replicate
import asyncio
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def run_model(image_url, prompt):

    output = await asyncio.to_thread(
        replicate.run,
        "stability-ai/sdxl",
        input={
            "image": image_url,
            "prompt": prompt,
            "strength": 0.35,
            "num_inference_steps": 30,
            "guidance_scale": 7
        }
    )

    return output


@bot.event
async def on_ready():
    print(f"Bot ready: {bot.user}")


# IMAGE EDIT COMMAND

@bot.command()
async def edit(ctx, *, prompt):

    if not ctx.message.attachments:
        await ctx.send("Upload an image with the command.")
        return

    image_url = ctx.message.attachments[0].url

    msg = await ctx.send("Editing image...")

    result = await run_model(image_url, prompt)

    await msg.delete()

    await ctx.send(result[0])


# BLEND TWO IMAGES

@bot.command()
async def blend(ctx, *, prompt):

    if len(ctx.message.attachments) < 2:
        await ctx.send("Upload TWO images.")
        return

    img1 = ctx.message.attachments[0].url
    img2 = ctx.message.attachments[1].url

    msg = await ctx.send("Blending images...")

    output = await asyncio.to_thread(
        replicate.run,
        "stability-ai/sdxl",
        input={
            "image": img1,
            "prompt": prompt + " combine with second image",
            "num_inference_steps": 30,
            "guidance_scale": 7
        }
    )

    await msg.delete()

    await ctx.send(output[0])


# HELP COMMAND

@bot.command()
async def help(ctx):

    text = """
AI Editing Bot

!edit <prompt>
Upload an image + edit instruction

Example:
!edit turn him into a cyberpunk soldier

!blend <prompt>
Upload two images to combine them
"""

    await ctx.send(text)


bot.run(TOKEN)
