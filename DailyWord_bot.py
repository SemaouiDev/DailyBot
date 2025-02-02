import requests
import random
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import logging
import asyncio

# Replace with your bot's token from BotFather
TOKEN = "7309166166:AAF6-R0FTBOimEmC3VOzeIfwqfcIxu29C1Y"
CHAT_ID = "7872499699"  # Add the chat ID where you want to send messages

# Setup logging to get some feedback in the console
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_random_word():
    """Fetch a random short English word (1-5 letters) from Datamuse API."""
    datamuse_url = "https://api.datamuse.com/words?ml=common&md=f&max=1000"
    response = requests.get(datamuse_url)
    words = response.json()

    word_list = [word["word"] for word in words if word["word"].isalpha() and 1 <= len(word["word"]) <= 5]
    return random.choice(word_list) if word_list else None

async def get_definition(word):
    """Fetch the definition of a word from the Free Dictionary API."""
    dictionary_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(dictionary_url)

    if response.status_code == 200:
        definition_data = response.json()
        return definition_data[0]["meanings"][0]["definitions"][0]["definition"]
    return "Definition not found."

async def send_word_to_chat(application: Application, context: CallbackContext) -> None:
    """Fetch a random word and send it to the predefined chat."""
    word = await get_random_word()
    if word:
        definition = await get_definition(word)
        message = f"**Word:** {word}\n**Definition:** {definition}"
    else:
        message = "Sorry, couldn't fetch a word. Try again later."

    # Send the word and definition to the chat using context.bot.send_message
    await context.bot.send_message(CHAT_ID, message, parse_mode="Markdown")

def start_scheduler(application: Application):
    """Start the scheduler to send words at specific times every day."""
    scheduler = BackgroundScheduler()

    # Wrap the async function to be called in the scheduler
    def send_word_job():
        # Create a new event loop for the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_word_to_chat(application, CallbackContext(application=application)))

    # Schedule the job to run at specific times every day
    scheduler.add_job(send_word_job, 'cron', hour=8, minute=0)   # 8:00 AM
    scheduler.add_job(send_word_job, 'cron', hour=12, minute=0)  # 12:00 PM
    scheduler.add_job(send_word_job, 'cron', hour=18, minute=0)  # 6:00 PM
    scheduler.add_job(send_word_job, 'cron', hour=22, minute=0)  # 10:00 PM

    scheduler.start()

def main():
    """Start the bot and scheduler."""
    # Create the Application
    app = Application.builder().token(TOKEN).build()

    # Start scheduler for sending words 4 times a day
    start_scheduler(app)

    # Start the bot
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()