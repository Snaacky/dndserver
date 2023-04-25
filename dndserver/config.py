from pyaml_env import BaseConfig, parse_config


config = BaseConfig(parse_config("config.yml"))
perks = parse_config("perks.yml")
