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

# ---------------- SAFE AI RUNNER ---------------- #

async def run_ai_model(model, inputs):
    try:
        output = replicate.run(model, input=inputs)

        if not output:
            return None

        if isinstance(output, list):
            return output

        return [output]

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


# ---------------- READY ---------------- #

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# ---------------- ERROR HANDLER ---------------- #

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ You forgot the prompt.")

    elif isinstance(error, commands.CommandNotFound):
        pass

    else:
        print(error)


# ---------------- BUTTON VIEW ---------------- #

class GridButtons(discord.ui.View):

    def __init__(self, prompt, images):
        super().__init__(timeout=None)
        self.prompt = prompt
        self.images = images

    async def upscale(self, interaction, index):

        await interaction.response.send_message("Upscaling...")

        output = await run_ai_model(
            "nightmareai/real-esrgan",
            {"image": self.images[index], "scale": 4}
        )

        if not output:
            await interaction.followup.send("Upscale failed.")
            return

        await interaction.followup.send(output[0])

    async def variation(self, interaction):

        await interaction.response.send_message("Generating variations...")

        images = []

        for i in range(4):

            out = await run_ai_model(
                "black-forest-labs/flux-schnell",
                {"prompt": self.prompt}
            )

            if out:
                images.append(out[0])

        if len(images) < 4:
            await interaction.followup.send("Variation failed.")
            return

        grid = create_grid(images)

        await interaction.followup.send(file=discord.File(grid))

    @discord.ui.button(label="U1", style=discord.ButtonStyle.green)
    async def u1(self, interaction, button):
        await self.upscale(interaction,0)

    @discord.ui.button(label="U2", style=discord.ButtonStyle.green)
    async def u2(self, interaction, button):
        await self.upscale(interaction,1)

    @discord.ui.button(label="U3", style=discord.ButtonStyle.green)
    async def u3(self, interaction, button):
        await self.upscale(interaction,2)

    @discord.ui.button(label="U4", style=discord.ButtonStyle.green)
    async def u4(self, interaction, button):
        await self.upscale(interaction,3)

    @discord.ui.button(label="V1", style=discord.ButtonStyle.blurple)
    async def v1(self, interaction, button):
        await self.variation(interaction)

    @discord.ui.button(label="V2", style=discord.ButtonStyle.blurple)
    async def v2(self, interaction, button):
        await self.variation(interaction)

    @discord.ui.button(label="V3", style=discord.ButtonStyle.blurple)
    async def v3(self, interaction, button):
        await self.variation(interaction)

    @discord.ui.button(label="V4", style=discord.ButtonStyle.blurple)
    async def v4(self, interaction, button):
        await self.variation(interaction)

    @discord.ui.button(label="🔄", style=discord.ButtonStyle.red)
    async def regen(self, interaction, button):

        await interaction.response.send_message("Regenerating...")

        images = []

        for i in range(4):

            out = await run_ai_model(
                "black-forest-labs/flux-schnell",
                {"prompt": self.prompt}
            )

            if out:
                images.append(out[0])

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

        out = await run_ai_model(
            "black-forest-labs/flux-schnell",
            {"prompt": prompt}
        )

        if out:
            images.append(out[0])

    grid = create_grid(images)

    await ctx.send(file=discord.File(grid))

    await ctx.send("Options:", view=GridButtons(prompt, images))


# ---------------- HQ GENERATION ---------------- #

@bot.command()
async def imaginehq(ctx, *, prompt):

    await ctx.send("Generating HQ images...")

    images = []

    for i in range(4):

        out = await run_ai_model(
            "black-forest-labs/flux-dev",
            {"prompt": prompt}
        )

        if out:
            images.append(out[0])

    grid = create_grid(images)

    await ctx.send(file=discord.File(grid))


# ---------------- MIX (IMPROVED) ---------------- #

@bot.command()
async def mix(ctx, *, prompt):

    if len(ctx.message.attachments) < 2:
        await ctx.send("Attach TWO images.")
        return

    img1_url = ctx.message.attachments[0].url
    img2_url = ctx.message.attachments[1].url

    await ctx.send("Mixing images...")

    img1 = Image.open(BytesIO(requests.get(img1_url).content))
    img2 = Image.open(BytesIO(requests.get(img2_url).content))

    img1 = img1.resize((512,512))
    img2 = img2.resize((512,512))

    combined = Image.new("RGB",(1024,512))

    combined.paste(img1,(0,0))
    combined.paste(img2,(512,0))

    path = "mix.jpg"
    combined.save(path)

    out = await run_ai_model(
        "stability-ai/sdxl",
        {
            "image": open(path,"rb"),
            "prompt": prompt,
            "strength":0.7
        }
    )

    if not out:
        await ctx.send("Mix failed.")
        return

    await ctx.send(out[0])


# ---------------- IMAGE EDIT ---------------- #

@bot.command()
async def accurateedit(ctx, *, prompt):

    if not ctx.message.attachments:
        await ctx.send("Attach image.")
        return

    img = ctx.message.attachments[0].url

    await ctx.send("Editing image...")

    out = await run_ai_model(
        "stability-ai/sdxl",
        {"image": img, "prompt": prompt}
    )

    if not out:
        await ctx.send("Edit failed.")
        return

    await ctx.send(out[0])


# ---------------- FACE EDIT ---------------- #

@bot.command()
async def editface(ctx, *, prompt):

    if not ctx.message.attachments:
        await ctx.send("Attach image.")
        return

    img = ctx.message.attachments[0].url

    await ctx.send("Editing face...")

    out = await run_ai_model(
        "stability-ai/sdxl",
        {"image": img, "prompt": prompt + ", focus on face"}
    )

    if not out:
        await ctx.send("Face edit failed.")
        return

    await ctx.send(out[0])


# ---------------- FACE SWAP ---------------- #

@bot.command()
async def faceswap(ctx):

    if len(ctx.message.attachments) < 2:
        await ctx.send("Attach TWO images.")
        return

    target = ctx.message.attachments[0].url
    face = ctx.message.attachments[1].url

    await ctx.send("Swapping faces...")

    out = await run_ai_model(
        "cjwbw/inswapper",
        {
            "target_image": target,
            "swap_image": face
        }
    )

    if not out:
        await ctx.send("Face swap failed.")
        return

    await ctx.send(out[0])


# ---------------- UPSCALE ---------------- #

@bot.command()
async def upscale(ctx):

    if not ctx.message.attachments:
        await ctx.send("Attach image.")
        return

    img = ctx.message.attachments[0].url

    await ctx.send("Upscaling...")

    out = await run_ai_model(
        "nightmareai/real-esrgan",
        {"image": img, "scale": 4}
    )

    if not out:
        await ctx.send("Upscale failed.")
        return

    await ctx.send(out[0])


# ---------------- RUN BOT ---------------- #

bot.run(TOKEN)
