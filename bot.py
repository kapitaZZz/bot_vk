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
        self.user_kb = self.keyboard.get_keyboard('main')

        self.main_keyboard = self.keyboard.get_keyboard('main')

        self.from_id = 0
        self.peer_id = 0
        self.msg = ''
        self.user_name = ''
        self.user_last_name = ''
        self.user_role = ''

        logging.info('Starting bot engine...')

    def get_user_name(self):
        result = self.vk.method('users.get', {'user_ids': self.from_id})
        user_name = result[0]['first_name']
        return user_name

    def get_user_last_name(self):
        result = self.vk.method('users.get', {'user_ids': self.from_id})
        user_last_name = result[0]['last_name']
        return user_last_name

    def get_document(self, path, type='doc', title='default document'):
        upload_url = self.vk_api.docs.getMessagesUploadServer(type=type, peer_id=self.peer_id)['upload_url']
        response = requests.post(upload_url, files={'file': open(path, 'rb')}).json()
        result = response['file']
        save = self.vk.method('docs.save', {'file': result, 'title': title})
        owner_id = save['doc']['owner_id']
        media_id = save['doc']['id']
        document = f'{type}{owner_id}_{media_id}'
        return document

    def check_user_in_db(self):
        sql = 'SELECT user_id FROM users_info WHERE user_id = %d' % self.from_id
        result = self.db.select_with_fetchone(sql)
        if result is None:
            return result
        else:
            result = str(result)
            result = result[1:-2]
        return result

    def add_user_in_db(self):
        sql = 'INSERT INTO users_info (user_id, user_name, user_last_name) VALUES (%d, "%s", "%s")' % \
              (self.from_id, self.user_name, self.user_last_name)
        self.db.query(str(sql))
        return True

    def send_msg(self, peer_id, msg, attachment: list = [], keyboard=None):
        self.vk.method('messages.send', {'peer_id': peer_id, 'message': msg, 'keyboard': keyboard,
                                         'attachment': attachment, 'random_id': 0})
        logging.info(f'id: {self.from_id} | name: {self.user_name} | message: {msg}')

    def send_spam(self):
        logging.info(f'Mailing started | from {self.from_id}')
        sql = "SELECT user_id FROM users_info"
        user_ids = [x[0] for x in self.db.select_with_fetchall(sql)]
        spam_sql = "SELECT user_last_message FROM users_info WHERE user_id = %d" % self.from_id
        spam_message = str(self.db.select_with_fetchone(spam_sql))
        spam_message = spam_message[2:-3:]
        message = f'Mailing created by {self.user_name} {self.user_last_name} \r\n {spam_message}'
        if spam_message == '':
            return self.send_msg(self.from_id, 'Message cannot be empty.')

        for id in user_ids:
            try:
                if id < 0:
                    continue
                self.send_msg(id, message)
                time.sleep(1)
            except Exception:
                spam_error_message = traceback.format.exc()
                logging.error(f'When mailing was raised an error {spam_error_message}')

        sql_reset = "UPDATE users_info SET user_last_message = 'waiting for message' WHERE user_id = %d" % self.from_id
        self.db.query(sql_reset)
        logging.info('Mailing completed.')

    def get_user_data(self):
        sql = "SELECT * FROM users_info WHERE user_id = '%s'" % self.from_id
        result = self.db.select_with_fetchone(sql)
        keys = ['id', 'user_id,', 'user_name', 'user_last_name', 'user_mode', 'user_role', 'user_last_message']
        data_keys = {}

        i = 0
        for key in keys:
            data_keys.update({key: result[i]})
            i += 1

        return data_keys

    def determinate_keyboard(self, path):
        if path == 'main':
            if self.user_role == "user":
                return self.user_kb
        return self.user_kb

    def start_bot(self):
        logging.info('Started main loop.')
        try:
            print("STARTING MAIN LOOP")
            for event in self.long_poll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    self.msg = event.obj['message']['text'].lower()
                    self.from_id = event.obj['message']['from_id']
                    self.peer_id = event.obj['message']['peer_id']
                    self.user_last_name = self.get_user_last_name()
                    self.user_name = self.get_user_name()

                    if self.check_user_in_db() is None:
                        self.add_user_in_db()
                    print(self.msg)
                    # doc = self.get_document(path='log/log.log')
                    # self.send_msg(self.peer_id, 'Log file', doc)

                    response = self.handler.msg_handler(self.get_user_data(), self.msg)
                    if response is False:
                        continue

                    if isinstance(response, tuple):
                        response_text = response[0]
                        response_kb = response[1]
                    else:
                        response_text = response
                        response_kb = None

                    if response_text == "off":
                        return "Off"

                    if response_text == 'spam':
                        self.send_spam()
                        continue

                    self.send_msg(self.from_id, response_text, keyboard=self.determinate_keyboard(response_kb))
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
