"""
Matndan rasm generatsiya qiluvchi Telegram bot — BEPUL versiya.
Pollinations.ai xizmati ishlatilgan.
"""

import io
import os
import random
import urllib.parse
from threading import Thread

import requests
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# --- Render uchun soxta veb-server ---
web_app = Flask(__name__)


@web_app.route('/')
def home():
    return "Bot ishlayapti!"


def run_web():
    web_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))


# --- Telegram bot qismi ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! 🎨\n"
        "Menga rasm tavsifini yuboring, men uni AI yordamida BEPUL chizib beraman.\n\n"
        "Foydalanish: /generate <tavsif>\n"
        "Masalan: /generate kosmosda uchayotgan pushti mushuk"
    )


def generate_image(prompt: str) -> bytes:
    encoded_prompt = urllib.parse.quote(prompt)
    seed = random.randint(0, 999999)

    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1024&seed={seed}&nologo=true"
    )

    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.content


async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)

    if not prompt:
        await update.message.reply_text(
            "Iltimos, tavsif yozing.\nMasalan: /generate qor bosgan tog'lar"
        )
        return

    status_msg = await update.message.reply_text("🎨 Rasm chizilmoqda, kuting...")

    try:
        image_bytes = generate_image(prompt)
        output = io.BytesIO(image_bytes)
        output.name = "generated.png"

        await update.message.reply_photo(photo=output, caption=f'Tavsif: "{prompt}"')
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"Xatolik yuz berdi: {e}")


def main():
    Thread(target=run_web).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
