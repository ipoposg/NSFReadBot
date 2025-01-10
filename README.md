
# NSF Read Bot

## Description
**NSF Read Bot** is a Python-based Telegram bot designed to help NSF personnel conveniently read books in camp through in-watch notifications. The bot streams book content in manageable chunks, making it easy to read while on the go.

This bot is accessible on Telegram via [@nsfbook_bot](https://t.me/nsfbook_bot).

## Features
- **Book Streaming**: Users can select from a curated collection of books, which are streamed in chunks suitable for reading through in-watch notifications.
- **Customisable Settings**: Modify settings such as word chunk size for a personalised reading experience.
- **Persistent Storage**: User preferences and progress are saved for continuity across sessions.
- **Asynchronous Design**: Ensures smooth and responsive interactions with the bot.

## How It Works
1. **Select a Book**: Browse a collection of available books and choose one to read.
2. **Read in Notifications**: The bot sends the book content in small, manageable sections via notifications.
3. **Track Your Progress**: Your reading progress is saved, so you can pick up where you left off.

## Installation (For Developers)
1. Clone the repository:
   ```bash
   git clone https://github.com/ipoposg/NSFReadBot.git

	2.	Navigate to the project directory:

cd NSFReadBot


	3.	Install the required dependencies:

pip install -r requirements.txt


	4.	Replace the placeholder in the script with your Telegram bot token:

BOT_TOKEN = "your-telegram-bot-token"


	5.	Run the bot:

python main.py



Usage (For Users)
	1.	Access the bot on Telegram: @nsfbook_bot.
	2.	Browse the available selection of books.
	3.	Select a book and begin reading through notifications.
	4.	Adjust the word chunk size if desired to customise your reading experience.

Folder Structure
	•	text_files/: Contains book files available for users.
	•	user_data.json: Stores user-specific data such as progress and preferences.

Dependencies
	•	Python 3.9+
	•	python-telegram-bot (Refer to requirements.txt for the complete dependency list).

## Contributing

Contributions are welcome! If you’d like to improve this bot, feel free to fork the repository, make changes, and submit a pull request.

## License

This project is licensed under the MIT License.
