from typing import Any, Type
from .module import Module


class Manifest:
    def __init__(self) -> None:
        self.manifest = {}
        self.type_manifest = {}
        pass

    def __getitem__(self, key: str | Type):
        if isinstance(key, str) and key in self.manifest:
            if key == "keys":
                return self.manifest.keys
            return self.manifest[key]
        elif isinstance(key, Type) and key in self.type_manifest:
            return self.type_manifest[key]
        return None

    def __getattr__(self, __name: str | Type) -> Any:
        if isinstance(__name, str) and __name in self.manifest:
            if __name == "keys":
                return self.manifest.keys
            return self.manifest[__name]
        elif isinstance(__name, Type) and __name in self.type_manifest:
            return self.type_manifest[__name]
        return None

    def __setitem__(self, __name: str, __value: Module) -> None:
        self.manifest[__name] = __value
        self.type_manifest[type(__value)] = __value
