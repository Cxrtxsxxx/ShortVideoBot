from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from moviepy.editor import *
import yt_dlp
import os

TOKEN = "7667187113:AAEomAK0-7zU2xwcrGU6HGW_exBODNblUO8"

# Fonction de découpe
def download_video(url, start_time, end_time):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Chercher le bon fichier téléchargé
    for ext in ['mp4', 'mkv', 'webm']:
        file_path = f'video.{ext}'
        if os.path.exists(file_path):
            clip = VideoFileClip(file_path)
            break
    else:
        raise Exception("Fichier vidéo introuvable")

    # Découper et convertir
    clip = clip.subclip(start_time, end_time)
    clip = clip.resize(height=1920, width=1080)
    clip.write_videofile("short.mp4", codec="libx264")
    
    return "short.mp4"

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Envoie-moi un lien YouTube avec les horaires comme :\nhttps://youtu.be/ID 00:15-00:45")

# Message texte
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "http" in text:
        try:
            url, times = text.split(' ')
            start_time, end_time = times.split('-')
            start_secs = int(start_time.split(':')[0]) * 60 + int(start_time.split(':')[1])
            end_secs = int(end_time.split(':')[0]) * 60 + int(end_time.split(':')[1])

            output_path = download_video(url, start_secs, end_secs)

            with open(output_path, 'rb') as video:
                await update.message.reply_video(video)

            # Nettoyer fichiers
            os.remove(output_path)
            for ext in ['mp4', 'mkv', 'webm']:
                file = f'video.{ext}'
                if os.path.exists(file):
                    os.remove(file)

        except Exception as e:
            await update.message.reply_text(f"Erreur : {e}")
    else:
        await update.message.reply_text("Format incorrect. Utilise : https://youtu.be/ID 00:15-00:45")

# Lancer le bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()