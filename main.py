from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from moviepy.editor import VideoFileClip
import yt_dlp
import os

# Ton token Telegram
TOKEN = "7667187113:AAEomAK0-7zU2xwcrGU6HGW_exBODNblUO8"

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bienvenue ! Envoie-moi un lien YouTube avec un intervalle, par exemple :\nhttps://youtu.be/ID 00:15-00:45")

# Fonction principale
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_input = update.message.text

        if "http" not in user_input or " " not in user_input:
            await update.message.reply_text("Format invalide. Utilise : https://youtu.be/ID 00:15-00:45")
            return

        url, times = user_input.split(" ")
        start_str, end_str = times.split("-")

        # Conversion en secondes
        start_time = int(start_str.split(":")[0]) * 60 + int(start_str.split(":")[1])
        end_time = int(end_str.split(":")[0]) * 60 + int(end_str.split(":")[1])

        await update.message.reply_text("Téléchargement de la vidéo...")

        # Télécharger la vidéo
        ydl_opts = {
            'outtmpl': 'video.mp4',
            'format': 'best'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Découpe avec MoviePy
        clip = VideoFileClip("video.mp4").subclip(start_time, end_time)
        clip = clip.resize(height=1920, width=1080)
        clip.write_videofile("short.mp4", codec="libx264", audio_codec="aac")

        # Envoi de la vidéo
        await update.message.reply_video(video=open("short.mp4", "rb"))

    except yt_dlp.utils.DownloadError:
        await update.message.reply_text("Erreur : impossible de télécharger la vidéo. Vérifie le lien.")
    except ValueError:
        await update.message.reply_text("Erreur de format. Utilise : https://youtu.be/ID 00:15-00:45")
    except Exception as e:
        await update.message.reply_text(f"Erreur : {str(e)}")
    finally:
        # Nettoyage
        if os.path.exists("video.mp4"):
            os.remove("video.mp4")
        if os.path.exists("short.mp4"):
            os.remove("short.mp4")

# Gestion des erreurs globales
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("Une erreur inattendue est survenue.")
    print(f"Erreur : {context.error}")

# Lancement du bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    app.run_polling()

if __name__ == "__main__":
    main()