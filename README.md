# Dndserver <a href="https://discord.gg/JdUWpdyvKr"><img src="https://discordapp.com/api/guilds/1098711487125672016/widget.png?style=shield"></a>

Dark and Darker private server implementation written in Python.

## Requirements

- [Playtest 5 beta files + hotfix 2 (0.5.0.1173)](https://discord.gg/darkanddarker)
- [Python](https://www.python.org/)
- [Poetry](https://python-poetry.org/)

## Install

- `git clone git@github.com:Snaacky/dndserver.git`
- `cd dndserver`
- `poetry install`
- `poetry shell`
- `python -m dndserver.server`
- Add `-server=dcweb.pages.dev:80` to your game's launch options.

## Docker quick start

### Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [Docker-compose](https://docs.docker.com/compose/install/)

### Start

> Note: The current startup script does not save data, and the data will be destroyed after restarting the container

- Copy `config.example.yml` to `config.yml`
- Build and start the service`docker-compose up --build`
- Add `-server=127.0.0.1:13337` to your game's launch options.

## Roadmap

Refer to [our project board](https://github.com/users/Snaacky/projects/4?query=is%3Aopen+sort%3Aupdated-desc).

## Contributing
Refer to [CONTRIBUTING.md](https://github.com/Snaacky/dndserver/blob/master/CONTRIBUTING.md)
