from saria.app import Module


class HandlerAlreadyExistsException:
    pass


class MessageHandlers(Module):
    def __init__(self):
        self.handlers = {}

    def register(self, handler: "MessageHandler"):
        if handler.name in self.handlers:
            raise HandlerAlreadyExistsException(
                f"Handler with name: {handler.name} is already registered."
            )
        self.handlers[handler.name] = handler

    def __iter__(self):
        return self.handlers.__iter__()
