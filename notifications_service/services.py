import os

import telebot

bot_token = os.environ["TELEGRAM_BOT_TOKEN"]

bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=["start"])
def send_telegram_notification(message):
    bot.send_message(message.chat.id, "Hello!")