# dndserver <a href="https://discord.gg/JdUWpdyvKr"><img src="https://discordapp.com/api/guilds/1098711487125672016/widget.png?style=shield"></a>

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
- `python -m alembic revision --autogenerate -m "Revision information go here"` Optional, only if you modify the database models
- `python -m alembic upgrade head` Creates database setting it to the latest revision
- `python -m dndserver.server`
- Add `-server=dcweb.pages.dev:80` to your game's launch options.

## Roadmap

Refer to [our project board](https://github.com/users/Snaacky/projects/4?query=is%3Aopen+sort%3Aupdated-desc).

## Contributing
Refer to [CONTRIBUTING.md](https://github.com/Snaacky/dndserver/blob/master/CONTRIBUTING.md)
