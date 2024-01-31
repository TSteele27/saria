import os
from typing import Any, Self
from dotenv import load_dotenv
from omegaconf import OmegaConf
from pathlib import Path
from saria.app import Module

load_dotenv(f"{os.getcwd()}/.env")
print(os.environ)


class Config(Module):
    def __init__(self):
        APP_ENV = os.environ["APP_ENV"] if "APP_ENV" in os.environ else "localhost"
        BASE_PATH = f"{os.getcwd()}/config"
        DEFAULT_CONFIG = f"{BASE_PATH}/default.config.yml"
        ENV_CONFIG = f"{BASE_PATH}/{APP_ENV.lower()}.config.yml"
        default_config = {}
        env_config = {}
        if Path(DEFAULT_CONFIG).is_file():
            default_config = OmegaConf.load(DEFAULT_CONFIG)
        if APP_ENV is not None and Path(ENV_CONFIG).is_file():
            env_config = OmegaConf.load(ENV_CONFIG)
        self.__cfg = OmegaConf.merge(default_config, env_config)

    def __getitem__(self: Self, key: str):
        if key == "keys":
            return self.__cfg.keys
        if key in self.__cfg:
            return self.__cfg[key]
        return None

    def __getattr__(self: Self, __name: str) -> Any:
        if __name == "keys":
            return self.__cfg.keys
        if __name in self.__cfg:
            return self.__cfg[__name]
        return None
