from typing import Self


class App:
    def __init__(self: Self, bundle: "Bundle"):
        from .injector import inject_dependencies
        from .bundle import Bundle
        from .config import Config

        self.bundle = Bundle(
            config=Config,
            app=self,
        ).extend(**bundle)
        self.manifest = inject_dependencies(self.bundle)
