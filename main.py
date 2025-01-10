import os
import json
import time
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Global token
BOT_TOKEN = ""

# Store user tasks globally
user_tasks = {}

# Paths
TEXT_FILES_FOLDER = "text_files"
USER_DATA_FILE = "user_data.json"

# Default settings
DEFAULT_RATE = 20  # Words per chunk
DEFAULT_INTERVAL = 10  # Seconds between messages

# Load or initialize user data
if os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "r") as f:
        user_data = json.load(f)
else:
    user_data = {}

# Save user data to file
def save_user_data():
    with open(USER_DATA_FILE, "w") as f:
        json.dump(user_data, f, indent=4)

# Enable debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Hello, {user.first_name}! Welcome to the Book Reader Bot 📚.\n"
        "Use /list to see available books.\n"
        "Use /read to start reading a book.\n"
        "Use /stop to bookmark your progress.\n"
        "You can also reread a book with the /reread command."
    )

# List available books
async def list_books(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    books = [f for f in os.listdir(TEXT_FILES_FOLDER) if f.endswith(".txt")]
    if not books:
        await update.message.reply_text("No books available in the folder.")
        return

    keyboard = [[InlineKeyboardButton(book, callback_data=f"book_{book}")] for book in books]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Available books:", reply_markup=reply_markup)

# Callback for book selection
async def book_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    book_name = query.data.replace("book_", "")
    user_id = str(query.from_user.id)

    user_data[user_id] = {
        "book": book_name,
        "position": 0,
        "rate": DEFAULT_RATE,
        "interval": DEFAULT_INTERVAL,
    }
    save_user_data()

    await query.message.reply_text(
        f"Selected book: {book_name}\n"
        f"Default output rate: {DEFAULT_RATE} words per message.\n"
        f"Default interval: {DEFAULT_INTERVAL} seconds between messages.\n"
        "Use /setrate and /setinterval to customize. Use /read to begin."
    )

# Set reading rate
async def set_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    if user_id not in user_data:
        await update.message.reply_text("Please select a book first using /list.")
        return

    try:
        rate = int(context.args[0])
        user_data[user_id]["rate"] = rate
        save_user_data()
        await update.message.reply_text(f"Output rate set to {rate} words per message.")
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid word count (e.g., /setrate 15).")

# Set message interval
async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    if user_id not in user_data:
        await update.message.reply_text("Please select a book first using /list.")
        return

    try:
        interval = int(context.args[0])
        user_data[user_id]["interval"] = interval
        save_user_data()
        await update.message.reply_text(f"Message interval set to {interval} seconds.")
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid interval (e.g., /setinterval 10).")

async def start_reading(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    if user_id not in user_data:
        await update.message.reply_text("Please select a book first using /list.")
        return

    # Check if a task is already running for this user
    if user_id in user_tasks and not user_tasks[user_id].done():
        await update.message.reply_text("You are already reading a book! Use /stop to stop reading.")
        return

    book_name = user_data[user_id]["book"]
    rate = user_data[user_id]["rate"]
    interval = user_data[user_id]["interval"]
    position = user_data[user_id]["position"]

    book_path = os.path.join(TEXT_FILES_FOLDER, book_name)
    if not os.path.exists(book_path):
        await update.message.reply_text("Book not found.")
        return

    with open(book_path, "r", encoding="utf-8") as f:
        text = f.read()

    words = text.split()
    total_words = len(words)

    if position >= total_words:
        await update.message.reply_text(
            f"You have finished reading '{book_name}'!\n"
            "Use /reread to start again or /list to choose a new book."
        )
        return

    # Create and start the asynchronous task
    user_tasks[user_id] = asyncio.create_task(
        send_book_chunks(update, context, user_id, words, position, rate, interval, book_name)
    )
    await update.message.reply_text(
        f"Starting to read '{book_name}'. Use /stop to pause and bookmark."
    )
    

async def send_book_chunks(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id, words, position, rate, interval, book_name):
    total_words = len(words)
    time.sleep(5)

    while position < total_words:
        end_position = min(position + rate, total_words)
        chunk = " ".join(words[position:end_position])

        # Send the chunk
        await context.bot.send_message(chat_id=update.effective_chat.id, text=chunk)

        # Update the position and save it
        position = end_position
        user_data[user_id]["position"] = position
        save_user_data()

        # Debugging information
        logging.debug(f"User {user_id} - Position updated to {position}")

        # Wait for the next chunk interval
        await asyncio.sleep(interval)


async def stop_reading(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)

    if user_id not in user_data or user_id not in user_tasks:
        await update.message.reply_text("You haven't started reading any book yet.")
        return

    # Cancel the task if it's running
    if user_tasks[user_id] and not user_tasks[user_id].done():
        user_tasks[user_id].cancel()

    # Bookmark the position minus 30 words for context
    position = user_data[user_id]["position"]
    user_data[user_id]["position"] = max(0, position - 30)
    save_user_data()

    await update.message.reply_text("Reading stopped. Your progress has been bookmarked.")
    
# Reread a book
async def reread(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    if user_id not in user_data:
        await update.message.reply_text("Please select a book first using /list.")
        return

    user_data[user_id]["position"] = 0  # Reset position to the beginning
    save_user_data()

    await update.message.reply_text(
        f"You will now start rereading '{user_data[user_id]['book']}'.\n"
        "Use /read to begin again."
    )

# Main function
def main():
    # Create application instance
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", list_books))
    application.add_handler(CallbackQueryHandler(book_selection, pattern=r"^book_"))
    application.add_handler(CommandHandler("setrate", set_rate))
    application.add_handler(CommandHandler("setinterval", set_interval))
    application.add_handler(CommandHandler("read", start_reading))
    application.add_handler(CommandHandler("stop", stop_reading))
    application.add_handler(CommandHandler("reread", reread))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    # Ensure the text files folder exists
    if not os.path.exists(TEXT_FILES_FOLDER):
        os.makedirs(TEXT_FILES_FOLDER)
    main()
