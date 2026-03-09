import discord
from discord.ext import commands
import replicate
import asyncio
import requests
from PIL import Image
from io import BytesIO
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)


# -------- AI GENERATION -------- #

async def generate_images(prompt):

    output = await asyncio.to_thread(
        replicate.run,
        "black-forest-labs/flux-dev",
        input={
            "prompt": prompt,
            "num_outputs": 4,
            "num_inference_steps": 30,
            "guidance_scale": 7
        }
    )

    return output


# -------- UPSCALE -------- #

async def upscale_image(url):

    output = await asyncio.to_thread(
        replicate.run,
        "nightmareai/real-esrgan",
        input={
            "image": url,
            "scale": 4
        }
    )

    return output[0]


# -------- GRID CREATOR -------- #

def create_grid(urls):

    images = []

    for url in urls:
        r = requests.get(url)
        img = Image.open(BytesIO(r.content))
        images.append(img)

    w, h = images[0].size

    grid = Image.new("RGB",(w*2,h*2))

    grid.paste(images[0],(0,0))
    grid.paste(images[1],(w,0))
    grid.paste(images[2],(0,h))
    grid.paste(images[3],(w,h))

    path = "grid.jpg"
    grid.save(path)

    return path


# -------- BUTTON VIEW -------- #

class ImageButtons(discord.ui.View):

    def __init__(self, prompt, images):
        super().__init__(timeout=None)
        self.prompt = prompt
        self.images = images


    async def do_upscale(self, interaction, index):

        await interaction.response.send_message("Upscaling...")

        result = await upscale_image(self.images[index])

        await interaction.followup.send(result)


    async def do_variation(self, interaction):

        await interaction.response.send_message("Creating variations...")

        imgs = await generate_images(self.prompt)

        grid = create_grid(imgs)

        await interaction.followup.send(file=discord.File(grid))


    @discord.ui.button(label="U1", style=discord.ButtonStyle.green)
    async def u1(self, interaction, button):
        await self.do_upscale(interaction,0)

    @discord.ui.button(label="U2", style=discord.ButtonStyle.green)
    async def u2(self, interaction, button):
        await self.do_upscale(interaction,1)

    @discord.ui.button(label="U3", style=discord.ButtonStyle.green)
    async def u3(self, interaction, button):
        await self.do_upscale(interaction,2)

    @discord.ui.button(label="U4", style=discord.ButtonStyle.green)
    async def u4(self, interaction, button):
        await self.do_upscale(interaction,3)


    @discord.ui.button(label="V1", style=discord.ButtonStyle.blurple)
    async def v1(self, interaction, button):
        await self.do_variation(interaction)

    @discord.ui.button(label="V2", style=discord.ButtonStyle.blurple)
    async def v2(self, interaction, button):
        await self.do_variation(interaction)

    @discord.ui.button(label="V3", style=discord.ButtonStyle.blurple)
    async def v3(self, interaction, button):
        await self.do_variation(interaction)

    @discord.ui.button(label="V4", style=discord.ButtonStyle.blurple)
    async def v4(self, interaction, button):
        await self.do_variation(interaction)


    @discord.ui.button(label="🔄", style=discord.ButtonStyle.red)
    async def regen(self, interaction, button):

        await interaction.response.send_message("Regenerating...")

        imgs = await generate_images(self.prompt)

        grid = create_grid(imgs)

        await interaction.followup.send(file=discord.File(grid))


# -------- IMAGINE COMMAND -------- #

@bot.command()
async def imagine(ctx, *, prompt):

    msg = await ctx.send("🎨 Generating images...")

    images = await generate_images(prompt)

    grid = create_grid(images)

    await msg.delete()

    await ctx.send(
        file=discord.File(grid),
        view=ImageButtons(prompt, images)
    )


# -------- PING -------- #

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong")


# -------- START BOT -------- #

bot.run(TOKEN)
