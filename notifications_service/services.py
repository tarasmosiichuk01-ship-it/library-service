from decouple import config

import telebot

bot_token = config("TELEGRAM_BOT_TOKEN")
chat_id = config("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(bot_token)


def send_telegram_notification(message: str) -> None:
    bot.send_message(chat_id=chat_id, text=message)
