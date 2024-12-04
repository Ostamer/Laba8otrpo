import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

EMAIL, MESSAGE = range(2)


def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Здравствуйте! Пожалуйста, введите ваш email:")
    return EMAIL


def get_email(update: Update, context: CallbackContext) -> int:
    email = update.message.text
    if is_valid_email(email):
        context.user_data['email'] = email
        update.message.reply_text("Спасибо! Теперь введите текст сообщения:")
        return MESSAGE
    else:
        update.message.reply_text("Некорректный email. Попробуйте снова:")
        return EMAIL


def get_message(update: Update, context: CallbackContext) -> int:
    message_text = update.message.text
    user_email = context.user_data['email']

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_EMAIL
        msg["To"] = user_email
        msg["Subject"] = "Сообщение из Telegram-бота"
        msg.attach(MIMEText(message_text, "plain"))

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, user_email, msg.as_string())

        update.message.reply_text("Сообщение успешно отправлено!")
    except Exception as e:
        update.message.reply_text(f"Не удалось отправить сообщение: {e}")

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Операция отменена.")
    return ConversationHandler.END


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, get_email)],
            MESSAGE: [MessageHandler(Filters.text & ~Filters.command, get_message)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
