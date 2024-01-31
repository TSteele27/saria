from saria.app import Module


class MessageHandlers(Module):
    def __init__(self):
        self.handlers = []

    def register(handler:'MessageHandler'):
