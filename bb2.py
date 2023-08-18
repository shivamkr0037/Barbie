from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests

# Replace 'YOUR_TOKEN' with the token you got from BotFather
BOT_TOKEN = '6332876538:AAHVVD_FhDfp8nqxvpUt3dBCUDdIl-6CCec'

# API configuration
API_URL = "https://api.reload.app/api/v1/dating-chat/chat?"
API_HEADERS = {
    "User-Agent": "Dart/3.0 (dart:io)",
    "x-api-key": "w2Y-pHD20TP--tVbDo2D8-DYam4tbA",
    "Accept-Encoding": "gzip",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjM5NTA1OSwiaWF0IjoxNjkyMzc2ODQwLCJleHAiOjE2OTIzOTg0NDB9.SJeA4-UNsLtRW-CduTXY50VYIarDArPYvriq8TT2Anc",
    "Content-Type": "application/json; charset=utf-8"
}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hello! Send me a message and I'll reply back!")

def reply_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text

    data = {
        "name": "Barbie",
        "partnerName": "Honey",
        "gender": "female",
        "firstPersonality": 0.8997493734335839,
        "secondPersonality": 0.7781954887218044,
        "thirdPersonality": 0.9235588972431079,
        "relationship": "girlfriend",
        "messages": [{"role": "user", "content": user_message}]
    }

    response = requests.post(API_URL, headers=API_HEADERS, json=data)
    
    if response.status_code == 200:
        response_data = response.json()
        bot_reply = response_data.get('content', "Sorry, I couldn't process that.")
    else:
        bot_reply = "An error occurred while processing your request."
    
    update.message.reply_text(bot_reply)

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, reply_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
