import discord
from discord.ext import commands
import os
import replicate
import requests
from PIL import Image
from io import BytesIO

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- SAFE AI RUNNER (ANTI FREEZE) ---------------- #

async def run_ai_model(model, inputs):

    try:
        output = replicate.run(model, input=inputs)

        if not output:
            return None

        if isinstance(output, list):
            return output[0]

        return output

    except Exception as e:
        print("AI Error:", e)
        return None


# ---------------- GRID CREATOR ---------------- #

def create_grid(image_urls):

    images = []

    for url in image_urls:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        images.append(img)

    w, h = images[0].size

    grid = Image.new("RGB", (w*2, h*2))

    grid.paste(images[0], (0,0))
    grid.paste(images[1], (w,0))
    grid.paste(images[2], (0,h))
    grid.paste(images[3], (w,h))

    path = "grid.jpg"
    grid.save(path)

    return path


# ---------------- BOT READY ---------------- #

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# ---------------- BUTTON VIEW ---------------- #

class GridButtons(discord.ui.View):

    def __init__(self, prompt, images):
        super().__init__(timeout=None)
        self.prompt = prompt
        self.images = images

    async def upscale_image(self, interaction, index):

        await interaction.response.send_message("Upscaling image... 🔍")

        img = self.images[index]

        output = await run_ai_model(
            "nightmareai/real-esrgan",
            {"image": img, "scale": 4}
        )

        if not output:
            await interaction.followup.send("Upscale failed.")
            return

        await interaction.followup.send(output)

    async def variation(self, interaction):

        await interaction.response.send_message("Generating variation... 🎨")

        images = []

        for i in range(4):

            output = await run_ai_model(
                "black-forest-labs/flux-schnell",
                {"prompt": self.prompt}
            )

            if output:
                images.append(output)

        if len(images) < 4:
            await interaction.followup.send("Variation failed.")
            return

        grid = create_grid(images)

        await interaction.followup.send(file=discord.File(grid))

    @discord.ui.button(label="U1", style=discord.ButtonStyle.green)
    async def u1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.upscale_image(interaction,0)

    @discord.ui.button(label="U2", style=discord.ButtonStyle.green)
    async def u2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.upscale_image(interaction,1)

    @discord.ui.button(label="U3", style=discord.ButtonStyle.green)
    async def u3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.upscale_image(interaction,2)

    @discord.ui.button(label="U4", style=discord.ButtonStyle.green)
    async def u4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.upscale_image(interaction,3)

    @discord.ui.button(label="V1", style=discord.ButtonStyle.blurple)
    async def v1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.variation(interaction)

    @discord.ui.button(label="V2", style=discord.ButtonStyle.blurple)
    async def v2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.variation(interaction)

    @discord.ui.button(label="V3", style=discord.ButtonStyle.blurple)
    async def v3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.variation(interaction)

    @discord.ui.button(label="V4", style=discord.ButtonStyle.blurple)
    async def v4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.variation(interaction)

    @discord.ui.button(label="🔄", style=discord.ButtonStyle.red)
    async def regen(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message("Regenerating...")

        images = []

        for i in range(4):

            output = await run_ai_model(
                "black-forest-labs/flux-schnell",
                {"prompt": self.prompt}
            )

            if output:
                images.append(output)

        if len(images) < 4:
            await interaction.followup.send("Regeneration failed.")
            return

        grid = create_grid(images)

        await interaction.followup.send(file=discord.File(grid))


# ---------------- HELP ---------------- #

@bot.command()
async def helpai(ctx):

    await ctx.send("""
🤖 AI IMAGE BOT COMMANDS

!imagine <prompt>
!imaginehq <prompt>

!mix <prompt> (attach 2 images)

!accurateedit <prompt> (attach image)

!editface <prompt> (attach image)

!faceswap (attach 2 images)

!upscale (attach image)

!ping
""")


# ---------------- PING ---------------- #

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")


# ---------------- IMAGINE ---------------- #

@bot.command()
async def imagine(ctx, *, prompt):

    await ctx.send("Generating images...")

    images = []

    for i in range(4):

        output = await run_ai_model(
            "black-forest-labs/flux-schnell",
            {"prompt": prompt}
        )

        if output:
            images.append(output)

    if len(images) < 4:
        await ctx.send("Generation failed.")
        return

    grid = create_grid(images)

    await ctx.send(file=discord.File(grid))

    await ctx.send("Options:", view=GridButtons(prompt, images))


# ---------------- HIGH QUALITY ---------------- #

@bot.command()
async def imaginehq(ctx, *, prompt):

    await ctx.send("Generating HQ images...")

    images = []

    for i in range(4):

        output = await run_ai_model(
            "black-forest-labs/flux-dev",
            {"prompt": prompt}
        )

        if output:
            images.append(output)

    if len(images) < 4:
        await ctx.send("HQ generation failed.")
        return

    grid = create_grid(images)

    await ctx.send(file=discord.File(grid))


# ---------------- MIX ---------------- #

@bot.command()
async def mix(ctx, *, prompt):

    if len(ctx.message.attachments) < 2:
        await ctx.send("Attach TWO images.")
        return

    img1 = ctx.message.attachments[0].url
    img2 = ctx.message.attachments[1].url

    await ctx.send("Mixing images...")

    output = await run_ai_model(
        "black-forest-labs/flux-dev",
        {"prompt": prompt, "image": img1, "image2": img2}
    )

    if not output:
        await ctx.send("Mix failed.")
        return

    await ctx.send(output)


# ---------------- IMAGE EDIT ---------------- #

@bot.command()
async def accurateedit(ctx, *, prompt):

    if len(ctx.message.attachments) == 0:
        await ctx.send("Attach image.")
        return

    img = ctx.message.attachments[0].url

    await ctx.send("Editing image...")

    output = await run_ai_model(
        "stability-ai/sdxl",
        {"image": img, "prompt": prompt, "strength": 0.4}
    )

    if not output:
        await ctx.send("Edit failed.")
        return

    await ctx.send(output)


# ---------------- FACE EDIT ---------------- #

@bot.command()
async def editface(ctx, *, prompt):

    if len(ctx.message.attachments) == 0:
        await ctx.send("Attach image.")
        return

    img = ctx.message.attachments[0].url

    await ctx.send("Editing face...")

    output = await run_ai_model(
        "stability-ai/sdxl",
        {"image": img, "prompt": prompt + ", focus on face"}
    )

    if not output:
        await ctx.send("Face edit failed.")
        return

    await ctx.send(output)


# ---------------- FACE SWAP ---------------- #

@bot.command()
async def faceswap(ctx):

    if len(ctx.message.attachments) < 2:
        await ctx.send("Attach TWO images.")
        return

    target = ctx.message.attachments[0].url
    face = ctx.message.attachments[1].url

    await ctx.send("Swapping faces...")

    output = await run_ai_model(
        "arielreplicate/inswapper",
        {"target_image": target, "swap_image": face}
    )

    if not output:
        await ctx.send("Face swap failed.")
        return

    await ctx.send(output)


# ---------------- UPSCALE ---------------- #

@bot.command()
async def upscale(ctx):

    if len(ctx.message.attachments) == 0:
        await ctx.send("Attach image.")
        return

    img = ctx.message.attachments[0].url

    await ctx.send("Upscaling...")

    output = await run_ai_model(
        "nightmareai/real-esrgan",
        {"image": img, "scale": 4}
    )

    if not output:
        await ctx.send("Upscale failed.")
        return

    await ctx.send(output)


# ---------------- RUN BOT ---------------- #

bot.run(TOKEN)
