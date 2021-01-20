# body of bot
import traceback

import vk_api.vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
import time
import logging
import requests

from database import DataBase
from handler import Handler
from keyboard import Keyboard

logging.basicConfig(filename='log/log.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class VkBot:
    def __init__(self, token, group_id):
        """
        Bot body
        :param token: token from config
        :param group_id: group id from config
        """
        self.vk = vk_api.VkApi(token=token)  # longpoll config
        self.long_poll = VkBotLongPoll(self.vk, group_id)  # longpoll connection
        self.vk_api = self.vk.get_api()  # access to methods vk
        self.token = token

        self.db = DataBase('db/database.db')
        self.handler = Handler()
        self.keyboard = Keyboard()

        self.main_keyboard = self.keyboard.get_keyboard('main')

        self.from_id = 0
        self.peer_id = 0
        self.msg = ''
        self.user_name = ''
        self.user_last_name = ''
        self.user_role = ''

        logging.info('Starting bot engine...')

    def get_user_name(self):
        result = self.vk.method('users.get', {'users_ids': self.from_id})
        print(result)

    def get_user_last_name(self):
        pass

    def check_user_in_db(self):
        sql = 'SELECT user_id FROM users_info WHERE user_id=?', self.from_id
        result = self.db.select_with_fetchone(sql)
        print(result)

    def add_user_in_db(self, from_id):
        sql = 'INSERT INTO users_info (user_id, user_name, user_last_name) VALUES (?, ?, ?)', \
              str(from_id), str(self.get_user_name), str(self.get_user_last_name)
        self.db.query(sql)
        return True

    def send_msg(self, peer_id, msg, keyboard=None):
        self.vk.method('messages.send', {'peer_id': peer_id, 'message': msg, 'keyboard': keyboard, 'random_id': 0})
        print('sent')

    def start_bot(self):
        logging.info('Started main loop.')
        try:
            for event in self.long_poll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    self.msg = event.object['message']['text'].lower()
                    self.from_id = event.object['message']['from_id']
                    self.peer_id = event.object['message']['peer_id']

                    if self.check_user_in_db is not None:
                        self.add_user_in_db(self.from_id)

                    # response = self.handler.msg_handler(self.from_id, self.peer_id, self.msg)
                    # response_text = response[0]
                    # response_kb = response[1]

        except requests.exceptions.ReadTimeout:
            connection_error = traceback.format_exc()
            self.vk = ' '
            self.vk = vk_api.VkApi(token=self.token)
            logging.error(f'Connection error in BOT.PY\n: {connection_error}\n. Reloading....')
            time.sleep(15)

        except Exception:
            error_bot = traceback.format_exc()
            print(f'Error type in BOT.PY file - \n     {error_bot}\n. Reloading....')
            logging.error(f'Error type in BOT.PY file -     {error_bot}.')
            logging.info('Reloading....')
            time.sleep(5)
