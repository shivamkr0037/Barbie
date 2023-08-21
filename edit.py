from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import requests
import time

TOKEN = "6348173469:AAGdOKJkk70-eY1chqfKn60Nj-e66svIT5Q"

STYLES = {
    "33": "Ink",
    "29": "Fantasy Game",
    "32": "Chinese painting",
    "23": "Mystery Box",
    "26": "Anime 2",
    "34": "Film Landscapes",
    "24": "Athena Temple",
    "27": "Science Fiction",
    "31": "Fantasy Magic"
}

post_url = "https://sd-prod.fengyi.io/api/v1/img2img"
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "okhttp/4.10.0"
}

def upload_image(image_data: bytes) -> str:
    url = "https://sd-prod.fengyi.io/api/upload"
    headers_upload = {
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.10.0"
    }
    files = {
        "file": ("uploaded_image.jpg", image_data, "image/jpeg")
    }
    response = requests.post(url, headers=headers_upload, files=files)
    return response.json()

def start(update: Update, context: CallbackContext) -> None:
    welcome_message = (
        "Hello!\n"
        "I'm your Image Transformation bot. Here's how you can use me:\n"
        "/edit - Start the image editing process.\n"
        "Just reply to a photo with /edit, or after typing /edit send a photo.\n"
        "I'll then guide you through the process. 🎨\n"
        "/help - Get help on how to use me."
    )
    update.message.reply_text(welcome_message)

def help_command(update: Update, context: CallbackContext) -> None:
    help_message = (
        "How to use the bot:\n"
        "1. Reply to a photo with /edit, or type /edit and then send a photo.\n"
        "2. Choose a style.\n"
        "3. Type the transformation prompt (e.g., 'make this box pink').\n"
        "I'll then transform your image based on your choice. Enjoy! 🖌️"
    )
    update.message.reply_text(help_message)



def edit(update: Update, context: CallbackContext) -> None:
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        handle_photo_or_document(update, context, from_edit_command=True)
    else:
        context.user_data["state"] = "waiting_for_image"
        update.message.reply_text('Please send a photo to Transform.')

def handle_photo_or_document(update: Update, context: CallbackContext, from_edit_command=False) -> None:
    if from_edit_command:
        context.user_data["state"] = "waiting_for_image"
    
    if context.user_data.get("state") != "waiting_for_image":
        return

    if from_edit_command:
        file_id = update.message.reply_to_message.photo[-1].file_id
    else:
        file_id = update.message.photo[-1].file_id if update.message.photo else None

    if not file_id:
        update.message.reply_text("Please send a valid photo.")
        return

    file = context.bot.getFile(file_id)
    image_data = file.download_as_bytearray()

    # Notify user that image is being uploaded
    uploading_message = update.message.reply_text("Uploading and processing your image. Hang tight!")
    
    response_json = upload_image(image_data)
    img_file_id = response_json.get("filename")

    # Delete the previous 'uploading' message
    context.bot.delete_message(chat_id=update.message.chat_id, message_id=uploading_message.message_id)

    if not img_file_id:
        update.message.reply_text("Failed to upload the image.")
        return

    context.user_data["img_file_id"] = img_file_id

    keyboard = [[InlineKeyboardButton(STYLES[style_id], callback_data=style_id)] for style_id in STYLES]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("The image has been uploaded; now, choose a style:", reply_markup=reply_markup)
    context.user_data["state"] = "waiting_for_style"


def style_callback(update: Update, context: CallbackContext) -> None:
    if context.user_data.get("state") != "waiting_for_style":
        return

    query = update.callback_query
    style_id = query.data

    context.user_data["style_id"] = style_id

    query.answer()
    query.edit_message_text(text="Image style selected. Now, please type the transformation prompt (e.g., 'Change hair color to black').")

    context.user_data["state"] = "waiting_for_prompt"

def handle_prompt_after_style(update: Update, context: CallbackContext) -> None:
    current_state = context.user_data.get("state")
    
    if current_state == "completed":
        return

    if current_state != "waiting_for_prompt":
        return

    prompt = update.message.text
    context.user_data["prompt"] = prompt
    style_id = context.user_data["style_id"]
    img_file_id = context.user_data["img_file_id"]

    data = {
        "img_file_id": img_file_id,
        "img_weight": 0.8,
        "priority": 10,
        "prompt": prompt,
        "style": style_id,
        "style_id": style_id
    }

    start_time = time.time()
    response = requests.post(post_url, headers=headers, json=data)
    json_response = response.json()
    image_id = json_response["id"]
    generation_message = f"👨‍🎤 Requested by: {update.effective_user.first_name}\n" \
                         f"📷 Image Id: Generating...\n" \
                         f"🤖 Status: Generating\n" \
                         f"⚡ Style: {STYLES[style_id]}"
    sent_message = update.message.reply_text(generation_message)
    context.user_data["state"] = "completed"

    get_url = f"https://sd-prod.fengyi.io/api/v1/txt2img/{image_id}"
    status = "generating"
    while status != "done":
        time.sleep(1)
        response = requests.get(get_url, headers=headers)
        json_response = response.json()
        status = json_response["status"]

    end_time = time.time()
    time_taken = end_time - start_time
    image_url = json_response["urls"][0]
    response = requests.get(image_url)

    with open("transformed_image.png", "wb") as f:
        f.write(response.content)

    context.bot.send_photo(chat_id=update.message.chat_id, photo=open("transformed_image.png", 'rb'))
    context.bot.edit_message_text(chat_id=update.message.chat_id, message_id=sent_message.message_id, 
                                  text=f"👨‍🎤 Requested by: {update.effective_user.first_name}\n📷 Image Id: {image_id}\n🤖 Status: Done\n⚡ Style: {STYLES[style_id]}\n⏱ Time Taken: {time_taken:.2f} seconds")

def main() -> None:
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start, run_async=True))
    dp.add_handler(CommandHandler("help", help_command, run_async=True))
    dp.add_handler(CommandHandler("edit", edit, run_async=True))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo_or_document, run_async=True))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_prompt_after_style, run_async=True))
    dp.add_handler(CallbackQueryHandler(style_callback, run_async=True))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main(
