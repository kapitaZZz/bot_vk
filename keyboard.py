# keyboard config

class Keyboard:
    def __init__(self):
        pass

    def get_keyboard(self, path):
        with open(f'keyboard/{path}.json', 'r', encoding='utf-8') as kb:
            return kb.read()
