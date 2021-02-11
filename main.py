# main file

import time
import logging
import traceback

from config import TOKEN, group_id
from bot import VkBot

logging.info('Starting bot.....')

while True:
    try:
        bot = VkBot(TOKEN, group_id)
        response = bot.start_bot()

        if response == "off":
            logging.warning("Bot is shutting down...")
            break
        else:
            continue

    except Exception:
        error = traceback.format_exc()
        print(f'Error type in MAIN.PY file - \n     {error}\n. Reloading....')
        logging.error(f'Error type in MAIN.PY> file -     {error}.')
        logging.info('Reloading....')
        time.sleep(10)

logging.info('Script finished.')
