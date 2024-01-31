"""Bundle."""
from saria.app.module import Module
from typing import Any, Self


class Bundle:
    """Contains the prototypes and keys for your applications dependencies."""

    def __init__(self: Self, **kwargs):
        self.dependencies = kwargs

    def extend(self: Self, **kwargs) -> "Bundle":
        """
        Adds additional dependencies to the bundle.
        Any conflicting keys are replaced with new values.
        """
        self.dependencies = {
            **self.dependencies,
            **kwargs,
        }
        return self

    def bootstrap(self: Self) -> "App":
        from saria.app.app import App

        return App(bundle=self)

    def __iter__(self: Self):
        return iter(self.dependencies)

    def __getitem__(self: Self, key: str):
        if key in self.dependencies:
            return self.dependencies[key]
        return None

    def __getattr__(self: Self, __name: str) -> Any:
        if __name == "keys":
            return self.dependencies.keys
        if __name in self.dependencies:
            return self.dependencies[__name]
        return None

    def __setitem__(self: Self, __name: str, __value: Module) -> None:
        self.dependencies[__name] = __value
