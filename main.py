"""
Matndan rasm generatsiya qiluvchi Telegram bot — BEPUL versiya.

Bu yerda Pollinations.ai xizmati ishlatilgan — u to'liq bepul,
ro'yxatdan o'tish yoki API kalit talab qilmaydi.
"""

import io
import random
import urllib.parse
import requests

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")


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
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
