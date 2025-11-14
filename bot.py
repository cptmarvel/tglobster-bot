import os
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

import os
TOKEN = os.getenv("TOKEN")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = update.message.caption

    if not caption:
        await update.message.reply_text("Добавь текст к фото")
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = "input.jpg"
    await file.download_to_drive(file_path)

    img = Image.open(file_path)
    draw = ImageDraw.Draw(img)
    font_size = int(img.width * 0.1)
    font = ImageFont.truetype("Lobster-Regular.ttf", font_size)


    bbox = draw.textbbox((0, 0), caption, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (img.width - text_width) / 2
    y = img.height - text_height - 100

    draw.text((x+3, y+3), caption, font=font, fill="black")
    draw.text((x, y), caption, font=font, fill="white")

    output = "output.jpg"
    img.save(output)

    await update.message.reply_photo(photo=open(output, "rb"))

    os.remove(file_path)
    os.remove(output)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("Бот работает...")
app.run_polling()

