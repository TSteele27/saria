from typing import Self, Type


class Dependency:
    def __init__(self: Self, name: str, prototype: Type = None):
        self.name = name
        self.prototype = prototype
