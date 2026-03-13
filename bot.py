import asyncio
import time
import logging
import os

from config import BOT_TOKEN, DOWNLOADS_DIR, USER_RATE_LIMIT_PER_HOUR, MAX_FILE_SIZE_BYTES, ADMINS, DEFAULT_LANG
from downloader import download_media, DownloadResult

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("social-downloader-bot")

# simple in-memory counters
user_requests = {}
active_downloads = 0
download_lock = asyncio.Lock()

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً! أرسل رابط فيديو أو استعلم عبر نص.")

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أوامر: /start, /help")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_downloads
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("أرسل رابط أو نص للبحث.")
        return
    is_url = any(text.startswith(s) for s in ("http://", "https://", "www.", "youtu", "tiktok", "instagram", "facebook", "twitter", "x.com", "reddit"))
    if not is_url:
        query = f"ytsearch:{text}"
    else:
        query = text
    msg = await update.message.reply_text("اختر نوع التحميل...")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Video (best)", callback_data=f"dl|{query}|best")],
        [InlineKeyboardButton("Audio (mp3)", callback_data=f"dl|{query}|audio")],
        [InlineKeyboardButton("Cancel", callback_data="cancel")]
    ])
    await msg.edit_text("اختر نوع التحميل:", reply_markup=keyboard)

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_downloads
    q = update.callback_query
    await q.answer()
    data = q.data
    if data == "cancel":
        await q.edit_message_text("تم الإلغاء.")
        return
    if not data.startswith("dl|"):
        await q.edit_message_text("بيانات غير معروفة.")
        return
    _, raw_query, mode = data.split("|", 2)
    async with download_lock:
        active_downloads += 1
    try:
        m = await q.edit_message_text("بدء التنزيل...")
        extract_audio = (mode == "audio")
        format_selector = None
        if mode == "best":
            format_selector = "bestvideo+bestaudio/best"
        res = await download_media(raw_query, format_selector=format_selector, extract_audio=extract_audio)
        fp = res.filepath
        if res.meta.get("warning") == "file_too_large" or fp.stat().st_size > int(os.getenv("MAX_FILE_SIZE_BYTES", 150*1024*1024)):
            await q.edit_message_text("الملف كبير جداً. ارسلت معلومات للمشرف.")
            await q.message.reply_text(f"الملف جاهز على الخادم: {fp}")
        else:
            await q.edit_message_text("جارٍ رفع الملف إلى Telegram...")
            await q.message.reply_document(document=InputFile(fp), filename=fp.name)
            await q.edit_message_text("تم الرفع.")
    except Exception as e:
        logger.exception("Download failed")
        await q.edit_message_text(f"فشل التحميل: {e}")
    finally:
        async with download_lock:
            active_downloads -= 1

def main():
    token = os.getenv("BOT_TOKEN") or ""
    if not token:
        print("BOT_TOKEN not set. ضع التوكن في متغير البيئة BOT_TOKEN أو في .env")
        return
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
    app.add_handler(CallbackQueryHandler(callback_query_handler))
    print("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
