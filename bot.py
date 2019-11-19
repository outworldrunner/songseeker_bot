import logging
from urllib.request import urlopen

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, CallbackQueryHandler

from aud import recognition_audio
from conf import configuration, r
from lastfm import get_similar_artist, get_similar_track

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Привіт!\nВідправ мені голосовий запис із піснею і я тобі знайду її або напиши артиста або пісню (у форматі артист - назва)  і я знайду схожі для тебе')

def callback_hanlder(update, context):
    """Handle the user callback button."""
    data = update.callback_query.data
    chat_id = update.callback_query.message.chat.id
    msg_id = update.callback_query.message.message_id
    if 'find' in data:
        splited = data.split("_")
        id_track = splited[1].replace("$%^", " ")
        track = r.hget(id_track, "track").decode()
        splitedtrack = track.split("-")
        similar = get_similar_track(splitedtrack[0].strip(), splitedtrack[1].strip(), amount=10)

    similar = list(similar)
    if similar:
        text = f"Ось що я знайшов схоже на *{track}*:\n\n" + "\n".join(similar)
        context.bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode='markdown')
    else:
        context.bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="Нічого не знайдено", parse_mode='markdown')

def find(update, context):
    """Echo the user message."""
    msg = update.message.reply_text("Шукаю...")
    if "-" in update.message.text:
        splited = update.message.text.split('-')
        try:
            similar = get_similar_track(splited[0].strip(), splited[1].strip(), amount=10)
        except Exception as e:
            print(e)
            context.bot.edit_message_text(chat_id=msg['chat']['id'], message_id=msg['message_id'], text="Нічого не знайдено", parse_mode='markdown')
            return
    else:
        try:    
            similar = get_similar_artist(update.message.text, amount=20)
        except Exception as e:
            print(e)
            context.bot.edit_message_text(chat_id=msg['chat']['id'], message_id=msg['message_id'], text="Нічого не знайдено", parse_mode='markdown')
            return
    similar = list(similar)
    if similar:
        text = f"Ось що я знайшов схоже на *{update.message.text}*:\n\n" + "\n".join(similar)
        context.bot.edit_message_text(chat_id=msg['chat']['id'], message_id=msg['message_id'], text=text, parse_mode='markdown')
    else:
        context.bot.edit_message_text(chat_id=msg['chat']['id'], message_id=msg['message_id'], text="Нічого не знайдено", parse_mode='markdown')

def recognition(update, context):
    msg = update.message.reply_text("Розпізнаю...")
    fileobj = context.bot.get_file(file_id=update.message.voice.file_id)
    voice = urlopen(fileobj['file_path']).read()
    track, id_track = recognition_audio(voice)
    if track is not None:
        print(track, id_track)
        r.hmset(str(id_track), {"track": track})
        callback_data = "find_" + str(id_track)
        keyboard = [
            [InlineKeyboardButton("Знайти схожі", callback_data=callback_data)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.edit_message_text(chat_id=msg['chat']['id'], message_id=msg['message_id'], text=f"*{track}*", reply_markup=reply_markup, parse_mode='markdown')
    else:
        context.bot.edit_message_text(chat_id=msg['chat']['id'], message_id=msg['message_id'], text="Незрівнянний трек! Але я не можу знайти його 😔", parse_mode='markdown')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(configuration['BOT']['token'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, find))
    dp.add_handler(MessageHandler(Filters.voice, recognition))
    dp.add_handler(CallbackQueryHandler(callback_hanlder))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
