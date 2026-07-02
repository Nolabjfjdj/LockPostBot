import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from flask import Flask
from threading import Thread

# ── CONFIG ────────────────────────────────────────────────────────
ALLOWED_ROLE_ID = 1490696042809786528  # ← METS ICI L'ID DU ROLE AUTORISÉ

# ── Flask health server pour UptimeRobot ──────────────────────────
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ── Discord bot ───────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ── Bot prêt ──────────────────────────────────────────────────────
@bot.event
async def on_ready():
    synced = await bot.tree.sync()

    print(f"✅ {len(synced)} commande(s) synchronisée(s)")
    for command in synced:
        print(f"📌 Commande : /{command.name} | ID : {command.id}")

    print(f"✅ Connecté en tant que {bot.user} (ID: {bot.user.id})")

# ── Commande /lock ─────────────────────────────────────────────────
@bot.tree.command(name="lock", description="Verrouille ce post de forum")
async def lock(interaction: discord.Interaction):

    # ✅ Vérification du rôle par ID
    user_role_ids = [role.id for role in interaction.user.roles]

    if ALLOWED_ROLE_ID not in user_role_ids:
        await interaction.response.send_message(
            "❌ Tu n'as pas le rôle autorisé pour utiliser cette commande.",
            ephemeral=True
        )
        return

    channel = interaction.channel

    # Vérifie que la commande est dans un post de forum
    if not isinstance(channel, discord.Thread) or not isinstance(channel.parent, discord.ForumChannel):
        await interaction.response.send_message(
            "❌ Cette commande fonctionne uniquement dans un post de forum.",
            ephemeral=True
        )
        return

    # Message visible par tous
    await interaction.response.send_message("Post verrouillé ✅")

    # 🔒 Verrouille seulement (sans archiver)
    try:
        await channel.edit(locked=True)
    except discord.Forbidden:
        await interaction.followup.send(
            "❌ Je n'ai pas la permission de verrouiller ce post.",
            ephemeral=True
        )
        return

    # Supprime le message après 5 secondes
    await asyncio.sleep(5)
    try:
        msg = await interaction.original_response()
        await msg.delete()
    except (discord.NotFound, discord.Forbidden):
        pass

# ── Lancement ─────────────────────────────────────────────────────
if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()

    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise ValueError("Variable d'environnement DISCORD_TOKEN manquante !")

    bot.run(token)