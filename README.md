# dndserver <a href="https://discord.gg/JdUWpdyvKr"><img src="https://discordapp.com/api/guilds/1098711487125672016/widget.png?style=shield"></a>

Dark and Darker private server implementation written in Python.

## Features
* Login
* Registration
* Character creation
* Character deletion
* Loading into lobby
* High-roller leaderboard
* Perk and skill selection
* Inventory and stash
* Gathering hall
* Basic party support
* Basic merchant support
* Persistent characters and items
* ... and many more features in development!

## Requirements

- [Playtest 5 beta files + hotfix 2 (0.5.0.1173)](https://discord.gg/darkanddarker)
- [Python](https://www.python.org/)
- [Poetry](https://python-poetry.org/)

## Install

### Bare metal
- `git clone git@github.com:Snaacky/dndserver.git`
- `cd dndserver`
- `poetry install`
- `poetry shell`
- `alembic upgrade head` 
- `python -m dndserver.server`
- Add `-server=dcweb.pages.dev:80` to your game's launch options.

### Docker
* `wget https://raw.githubusercontent.com/Snaacky/dndserver/master/docker-compose.yml`
* `mkdir config && cd config`
* `wget https://raw.githubusercontent.com/Snaacky/dndserver/master/config.example.yml -O config.yml`
* `touch dndserver.db`
* `cd ..`
* `docker-compose up -d`
* `docker exec -it dndserver alembic upgrade head`
* `docker restart dndserver`

## Web server
Before the game client connects to the TCP lobby server (and later on the UDP game server) it first connects to an HTTP discovery server specified in the game's launch options using the `-server=address:port` schema to get the  TCP server address to connect to. The endpoint the client connects to is `/dc/helloWorld` and the server returns a JSON blob such as `{"ipAddress": "xx.xx.xx.xx", "port": 65535}`. To simplify the development process we are hosting an HTTP discovery server at `dcweb.pages.dev:80` to redirect your client traffic to `127.0.0.1` without having to host your own HTTP server.

## Demo instance
A demo instance is being hosted at `-server=dndserver.lol:80`. The demo instance will automatically pull new commits from the master branch so you can check out the latest developments without having to setup your own instance.
