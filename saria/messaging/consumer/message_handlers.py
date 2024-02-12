from saria.app import Module


class MessageHandlers(Module):
    def __init__(self):
        self.handlers = []

    def register(self, handler: "MessageHandler"):
        self.handlers.append(handler)
