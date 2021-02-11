# bot logic

import commands
from database import DataBase


class Handler:
    def __init__(self):
        self.from_id = 0
        self.peer_id = 0
        self.msg = ''

        self.db = DataBase('db/database.db')

        self.roles_info = self.get_roles()
        self.commands_info = self.get_commands()
        self.modes_info = self.get_modes()

    def get_commands(self):
        commands = {}
        sql = "SELECT command_name, command_access FROM commands"
        query = [x for x in self.db.select_with_fetchall(sql)]
        for i in query:
            commands.update({i[0]: i[1]})
        return commands

    def get_modes(self):
        modes = {}
        sql = "SELECT mode_name, mode_access FROM modes"
        query = [x for x in self.db.select_with_fetchall(sql)]
        for i in query:
            modes.update({i[0]: i[1]})
        return modes

    def get_roles(self):
        roles = {}
        sql = "SELECT * FROM roles"
        query = [x for x in self.db.select_with_fetchall(sql)]
        for i in query:
            roles.update({i[0]: i[1]})
        return roles

    def check_spam(self):
        sql = "SELECT user_mode FROM users_info WHERE user_mode = 'mailing'"
        result = self.db.select_with_fetchall(sql)
        if result == []:
            return True
        return False

    def say_hello(self):
        return "Привет!", 'main'

    def msg_handler(self, user_data, command):
        self.command = command
        self.command_text = ''
        self.id = user_data['id']
        self.user_id = user_data['user_id,']
        self.user_name = user_data['user_name']
        self.user_last_name = user_data['user_last_name']
        self.user_mode = user_data['user_mode']
        self.user_role = user_data['user_role']
        self.user_last_message = user_data['user_last_message']

        if self.command.startswith('[club201744395|@bot_api]'):  # TODO change here id group by default
            self.command = self.command[25::]
        if self.command.startswith('//'):
            params = self.command.split(' ', maxsplit=1)
            self.command = self.command[2::]
            try:
                self.command_text = params[1]
            except:
                self.command_text = self.command
            if self.command in self.modes_info:
                if self.modes_info[self.command] < self.roles_info[self.user_role]:
                    return self.change_user_mode(self.command)
                else:
                    return "Permission denied!"
            else:
                return "Unknown mode."
        elif self.command.startswith('/'):
            params = self.command.split(' ', maxsplit=1)
            self.command = self.command[2::]
            try:
                self.command_text = params[1]
            except:
                self.command_text = self.command
            if self.command in self.modes_info:
                if self.commands_info[self.command] < self.roles_info[self.user_role]:
                    return self.processor(self.command)
                else:
                    return "Permission denied!"
            else:
                return "Unknown mode."
        elif command == "начать":
            return self.say_hello()
        else:
            return False

    def processor(self):
        if self.user_mode == "default":
            return 1, 'main'
        elif self.user_mode == "mailing":
            if self.command == "создать_рассылку":
                sql = "UPDATE users_info SET user_last_message = 'waiting for message' WHERE user_id = %d" % self.user_id
                self.db.query(sql)
                return 'Input text for mailing.'
            elif self.user_last_message == 'waiting for message':
                sql = "UPDATE users_info SET user_last_message = '%s' WHERE user_id = %d" % (self.command, self.user_id)
                self.db.query(sql)
                return 'Text saved.'
            elif self.command == 'очистить_текст':
                sql = "UPDATE users_info SET user_last_message = 'waiting for message' WHERE user_id = %d" % self.user_id
                self.db.query(sql)
                return 'Text deleted'
            elif self.command == 'разослать':
                if self.user_last_message == '':
                    return 'Message cannot be empty.'
                elif self.user_last_message == 'waiting for message':
                    return 'Cannot find saved text.'
                else:
                    return 'spam'
        else:
            return "Mode does not exists."

    def change_user_mode(self, mode):
        if mode == self.user_mode:
            return "You are in current mode."
        elif mode == "mailing":
            if self.check_spam():
                sql = "UPDATE users_info SET user_mode = 'mailing' WHERE user_id = %d" % self.user_id
                self.db.query(sql)
                return "Mode updated."
            else:
                return "Somebody in this mode, try again later."
        elif mode == "default":
            sql = "UPDATE users_info SET user_mode = 'default', user_last_message = 'None' WHERE user_id = %d" % self.user_id
            self.db.query(sql)
            return "Mode updated."
        else:
            return "Required mode does not exists."
