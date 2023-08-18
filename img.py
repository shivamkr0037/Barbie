import requests
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, run_async

# Get this from @BotFather
TOKEN = "1155338187:AAGaXuFeKWnWHSVXMSWKeUzW9M6v9X94JIM"

url = "https://sd-prod.fengyi.io/api/v1/txt2img"
headers = {
    "Host": "sd-prod.fengyi.io",
    "Content-Type": "application/json; charset=utf-8",
    "Accept-Encoding": "gzip",
    "User-Agent": "okhttp/4.10.0"
}

styles = {
    "Dreamy Portrait": "1",
    "Anime V2": "2",
    "Cyberpunk": "3",
    "VFX": "7",
    "CG": "10",
    "Flat": "11",
    "Alphonse Mucha": "12",
    "Van gogh": "13",
    "Picasso": "14",
    "Edward Hopper": "15",
    "Watercolor": "16",
    "Abstract Drawing": "17",
    "Ghibli": "18",
    "Chinese painting": "19",
    "Ink": "20",
    "Colorful World": "21",
    "Film Landscapes": "22"
}

@run_async
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! 🤗 /photo to Start generating an image 🖼️')

@run_async
def photo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('What kind of image would you like to generate? 🤔 Describe it using phrases separated by commas in English.')

@run_async
def handle_prompt(update: Update, context: CallbackContext) -> None:
    context.user_data["prompt_text"] = update.message.text
    keyboard = [[InlineKeyboardButton(style, callback_data=style_id)] for style, style_id in styles.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Choose a style:', reply_markup=reply_markup)

@run_async
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    style_value = query.data

    data = {
        "img_file_id": "",
        "img_weight": 0.8,
        "priority": 10,
        "prompt": context.user_data["prompt_text"],
        "style": style_value,
        "style_id": style_value
    }

    query.edit_message_text(text="Generating your image 🖼️ - almost done! Please wait a few seconds...")
    response = requests.post(url, headers=headers, json=data)
    json_response = response.json()
    image_id = json_response["id"]
    get_url = f"https://sd-prod.fengyi.io/api/v1/txt2img/{image_id}"

    status = "generating\"
    while status != "done":
        response = requests.get(get_url, headers=headers)
        json_response = response.json()
        status = json_response["status"]
        time.sleep(1)  # Blocking sleep for 1 second

    image_url = json_response["urls"][0]
    image_response = requests.get(image_url, headers=headers)

    file_name = f"{image_id}.png"
    with open(file_name, "wb") as f:
        f.write(image_response.content)

    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=open(file_name, 'rb'))
    query.edit_message_text(text=f"Done! Your unique image 🖼️ with ID {image_id}.png has been generated and sent to you!")

@run_async
def gen(update: Update, context: CallbackContext) -> None:
    prompt_text = " ".join(context.args)  # This will get the text after the /gen command
    if not prompt_text:  # If no text is provided, give an error message
        update.message.reply_text("Please provide a description after the /gen command.")
        return

    style_value = styles["Anime V2"]  # Default style for /gen command

    data = {
        "img_file_id": "",
        "img_weight": 0.8,
        "priority": 10,
        "prompt": prompt_text,
        "style": style_value,
        "style_id": style_value
    }

    update.message.reply_text("Generating your image 🖼️ - almost done! Please wait a few seconds...")
    response = requests.post(url, headers=headers, json=data)
    json_response = response.json()
    image_id = json_response["id"]
    get_url = f"https://sd-prod.fengyi.io/api/v1/txt2img/{image_id}"

    status = "generating"
    while status != "done":
        response = requests.get(get_url, headers=headers)
        json_response = response.json()
        status = json_response["status"]
        time.sleep(1)  # Blocking sleep for 1 second

    image_url = json_response["urls"][0]
    image_response = requests.get(image_url, headers=headers)

    file_name = f"{image_id}.png"
    with open(file_name, "wb") as f:
        f.write(image_response.content)

    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=open(file_name, 'rb'))
    query.edit_message_text(f"Done! Your unique image 🖼️ with ID {image_id}.png has been generated and sent to you!")

def main() -> None:
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start, run_async=True))
    dp.add_handler(CommandHandler("photo", photo, run_async=True))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_prompt, run_async=True))
    dp.add_handler(CallbackQueryHandler(button, run_async=True))
    dp.add_handler(CommandHandler("gen", gen, pass_args=True, run_async=True))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
