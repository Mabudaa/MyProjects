import threading
from api import app
from bot_script import bot
import MetaTrader5 as mt5

def initialize_metatrader():
    while True:
        if mt5.initialize():
            print("MetaTrader initialized successfully.")
            break 
        else:
            print("Failed to initialize MetaTrader. Retrying in 5 seconds...")
            time.sleep(3)

def start_api():
	app.run(host = '', port = '')

def start_bot():
	bot()

if __name__ == '__main__':
	initialize_metatrader()
	api_thread = threading.Thread(target=start_api)
	bot_thread = threading.Thread(target=start_bot)

	api_thread.start()
	bot_thread.start()

	api_thread.join()
	bot_thread.join()