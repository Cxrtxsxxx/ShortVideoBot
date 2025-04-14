import os
import yt_dlp
from moviepy.editor import * VideoFileClip
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = '7667187113:AAEomAK0-7zU2xwcrGU6HGW_exBODNblUO8'

# Fonction de téléchargement et découpage
def download_video(url, start_time, end_time):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Trouve le fichier téléchargé
    video_file = next((f for f in os.listdir('.') if f.startswith('video.')), None)

    # Découpe vidéo
    clip = VideoFileClip(video_file)
    clip = clip.subclip(start_time, end_time)
    clip = clip.resize(height=1920, width=1080)  # Format vertical
    clip.write_videofile("short.mp4", codec='libx264')

    return "short.mp4"

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Envoie un lien YouTube avec les horaires :\nExemple : https://youtu.be/ID 00:15-00:45")

# Gestion des messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "http" in text:
        try:
            url, times = text.split(' ')
            start_str, end_str = times.split('-')
            start = int(start_str.split(':')[0]) * 60 + int(start_str.split(':')[1])
            end = int(end_str.split(':')[0]) * 60 + int(end_str.split(':')[1])

            video_path = download_video(url, start, end)
            await update.message.reply_video(video=open(video_path, 'rb'))

        except Exception as e:
            await update.message.reply_text(f"Erreur : {str(e)}")

# Fonction principale
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
