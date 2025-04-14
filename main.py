import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import yt_dlp
import moviepy as mp
import os
from tempfile import NamedTemporaryFile

# Remplace par ton token Telegram
TOKEN ='7667187113:AAEomAK0-7zU2xwcrGU6HGW_exBODNblUO8'

# Fonction de téléchargement de la vidéo
def download_video(url, start_time, end_time):
    # Téléchargement vidéo
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_url = info_dict['formats'][0]['url']
        file_extension = video_url.split('.')[-1]
        file_path = f"video.{file_extension}"
        ydl.download([url])

    # Découpe vidéo avec MoviePy
    clip = mp.VideoFileClip(file_path)
    clip = clip.subclip(start_time, end_time)
    clip = clip.resize(height=1920, width=1080)  # Format vertical
    clip.write_videofile('short.mp4', codec='libx264')

    return 'short.mp4'

# Fonction qui gère les messages
def start(update, context):
    update.message.reply_text("Envoyez-moi un lien YouTube avec les horaires comme 'https://youtu.be/ID 00:15-00:45'")

def handle_message(update, context):
    user_input = update.message.text
    if "http" in user_input:
        try:
            url, times = user_input.split(' ')
            start_time, end_time = times.split('-')
            start_time = int(start_time.split(':')[0])*60 + int(start_time.split(':')[1])  # Convert to seconds
            end_time = int(end_time.split(':')[0])*60 + int(end_time.split(':')[1])
            video_path = download_video(url, start_time, end_time)
            context.bot.send_video(chat_id=update.message.chat_id, video=open(video_path, 'rb'))
        except Exception as e:
            update.message.reply_text("Erreur dans la commande, assurez-vous de bien entrer l'URL et les horaires au format 'https://youtu.be/ID 00:15-00:45'")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()