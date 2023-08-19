import requests
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, run_async

# Get this from @BotFather
TOKEN = "6470616589:AAFUAfk0EllT9K2RU5x4KFhvUz9INcmRbEI"

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
    context.user_data["expecting_description"] = True


@run_async
def handle_prompt(update: Update, context: CallbackContext) -> None:
    if "expecting_description" in context.user_data and context.user_data["expecting_description"]:
        context.user_data["prompt_text"] = update.message.text
        keyboard = [[InlineKeyboardButton(style, callback_data=style_id)] for style, style_id in styles.items()]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Choose a style:', reply_markup=reply_markup)
        context.user_data["expecting_description"] = False  # Reset the flag
    else:
        # Handle any other non-command text messages if needed
        pass


@run_async
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    style_value = query.data
    style_name = [name for name, id in styles.items() if id == style_value][0]  # Get the style name by its value

    data = {
        "img_file_id": "",
        "img_weight": 0.8,
        "priority": 10,
        "prompt": context.user_data["prompt_text"],
        "style": style_value,
        "style_id": style_value
    }

    generation_message = f"👨‍🎤 Requested by: {update.effective_user.first_name}\n" \
                         f"📷 Image Id: Generating...\n" \
                         f"🤖 Status: Generating\n" \
                         f"⚡ Style: {style_name}"
    query.edit_message_text(text=generation_message)

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
    query.edit_message_text(text=f"👨‍🎤 Requested by: {update.effective_user.first_name}\n📷 Image Id: {image_id}\n🤖 Status: Done\n⚡ Style: {style_name}")

@run_async
def gen(update: Update, context: CallbackContext) -> None:
    prompt_text = " ".join(context.args)
    if not prompt_text:
        update.message.reply_text("Please provide a description after the /gen command.")
        return

    style_value = styles["Anime V2"]
    style_name = [name for name, id in styles.items() if id == style_value][0]

    data = {
        "img_file_id": "",
        "img_weight": 0.8,
        "priority": 10,
        "prompt": prompt_text,
        "style": style_value,
        "style_id": style_value
    }

    generation_message = f"👨‍🎤 Requested by: {update.effective_user.first_name}\n" \
                         f"📷 Image Id: Generating...\n" \
                         f"🤖 Status: Generating\n" \
                         f"⚡ Style: {style_name}"
    sent_message = update.message.reply_text(generation_message)

    response = requests.post(url, headers=headers, json=data)
    json_response = response.json()
    image_id = json_response["id"]
    get_url = f"https://sd-prod.fengyi.io/api/v1/txt2img/{image_id}"

    status = "generating"
    while status != "done":
        response = requests.get(get_url, headers=headers)
        json_response = response.json()
        status = json_response["status"]
        time.sleep(1)

    image_url = json_response["urls"][0]
    image_response = requests.get(image_url, headers=headers)

    file_name = f"{image_id}.png"
    with open(file_name, "wb") as f:
        f.write(image_response.content)

    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=open(file_name, 'rb'))
    context.bot.edit_message_text(chat_id=chat_id, message_id=sent_message.message_id, 
                                  text=f"👨‍🎤 Requested by: {update.effective_user.first_name}\n📷 Image Id: {image_id}\n🤖 Status: Done\n⚡ Style: {style_name}")


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
    main(
