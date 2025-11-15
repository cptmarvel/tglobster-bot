import os
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = "@xyun9i_bot"

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.message.chat.type

    if chat_type not in ['group', 'supergroup']:
        caption = update.message.caption
        if not caption:
            await update.message.reply_text("Добавь текст к фото")
            return
        photo = update.message.photo[-1]
    else:
        caption = None
        photo = None

        if (update.message.caption and 
            BOT_USERNAME.lower() in update.message.caption.lower()):
            caption = update.message.caption.lower().replace(BOT_USERNAME.lower(), '').strip()
            if not caption:
                await update.message.reply_text(f"Добавь текст после {BOT_USERNAME}")
                return
            photo = update.message.photo[-1]

        elif (update.message.reply_to_message and
              update.message.reply_to_message.photo and
              update.message.text and
              BOT_USERNAME.lower() in update.message.text.lower()):
            caption = update.message.text.lower().replace(BOT_USERNAME.lower(), '').strip()
            if not caption:
                await update.message.reply_text(f"Добавь текст после {BOT_USERNAME}")
                return
            photo = update.message.reply_to_message.photo[-1]
        else:
            return

    if not photo:
        return

    file = await photo.get_file()
    file_path = "input.jpg"
    await file.download_to_drive(file_path)

    try:
        img = Image.open(file_path)
        draw = ImageDraw.Draw(img)
        font_size = int(img.width * 0.1)
        font = ImageFont.truetype("Lobster-Regular.ttf", font_size)

        bbox = draw.textbbox((0, 0), caption, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (img.width - text_width) / 2
        y = img.height - text_height - 80

        draw.text((x+3, y+3), caption, font=font, fill="black")
        draw.text((x, y), caption, font=font, fill="white")

        output = "output.jpg"
        img.save(output)
        await update.message.reply_photo(photo=open(output, "rb"))
    except Exception as e:
        await update.message.reply_text(f"Ошибка при обработке изображения: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(output):
            os.remove(output)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("Бот работает...")

app.run_polling()

