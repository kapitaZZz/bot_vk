# bot logic


class Handler:
    def __init__(self):
        self.from_id = 0
        self.peer_id = 0
        self.msg = ''

    def msg_handler(self, user_id, peer_id, msg):
        self.user_id = user_id
        self.peer_id = peer_id
        self.msg = msg
        if self.msg == '/help':
            return 'help text'
        else:
            return 'None', 'main'
