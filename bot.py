import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from flask import Flask
from threading import Thread

# ── Flask health server pour UptimeRobot ──────────────────────────────────────
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ── Discord bot ───────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Connecté en tant que {bot.user} (ID: {bot.user.id})")

@bot.tree.command(name="lock", description="Verrouille ce post de forum")
@app_commands.checks.has_permissions(manage_threads=True)
async def lock(interaction: discord.Interaction):
    channel = interaction.channel

    # Vérifie que la commande est bien dans un post de forum
    if not isinstance(channel, discord.Thread) or not isinstance(channel.parent, discord.ForumChannel):
        await interaction.response.send_message(
            "❌ Cette commande fonctionne uniquement dans un post de forum.",
            ephemeral=True
        )
        return

    # Envoie le message visible par tous
    await interaction.response.send_message("Post verrouillé ✅")

    # Verrouille le thread du forum
    try:
        await channel.edit(locked=True, archived=True)
    except discord.Forbidden:
        pass

    # Attend 5 secondes puis supprime le message
    await asyncio.sleep(5)
    try:
        msg = await interaction.original_response()
        await msg.delete()
    except (discord.NotFound, discord.Forbidden):
        pass

@lock.error
async def lock_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ Tu n'as pas la permission de verrouiller ce post.",
            ephemeral=True
        )

# ── Lancement ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()

    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise ValueError("Variable d'environnement DISCORD_TOKEN manquante !")
    bot.run(token)
