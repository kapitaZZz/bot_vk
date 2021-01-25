# bot logic

import commands
from database import DataBase


class Handler:
    def __init__(self):
        self.from_id = 0
        self.peer_id = 0
        self.msg = ''

    def msg_handler(self, user_data, command):
        self.id = user_data['id']
        # self.user_id = user_data['user_id']
        self.user_name = user_data['user_name']
        self.user_last_name = user_data['user_last_name']
        self.user_mode = user_data['user_mode']
        self.user_role = user_data['user_role']
        self.user_last_message = user_data['user_last_message']

        self.db = DataBase('db/database.db')

        self.command = command
        self.command_text = ''

        if command.startswith('//'):
            pass
        elif command.startswith('/'):
            self.command_text = self.command[1::]
            if self.user_role == 'user':
                if self.command_text in commands.user_access_list:
                    pass
                else:
                    return 'unknown command'
            elif self.user_role == 'Editor':
                if self.command_text in commands.Editor_access_list:
                    pass
                else:
                    return 'unknown command'
            elif self.user_role == 'ADMIN':
                if self.command_text in commands.ADMIN_access_list:
                    pass
                else:
                    return 'unknown command'
            elif self.user_role == 'ROOT':
                if self.command_text in commands.ROOT_access_list:
                    return self.processor(), 'main'
                else:
                    return 'unknown command'
            else:
                return 'unknown user'
        else:
            return 'unknown command'

    def processor(self):
        if self.command_text == 'начать':
            return 'Привет!'

    def change_user_mode(self):
        pass