# Installation

## Requirements

### Assumptions

- You have the rights to install pips
- You are in the root dir of this module

Yum

- gcc
- python3-devel

Python 3

```shell
pip install -r Pipfile
```

### Permissions

- Defaults

``` shell
find $PWD -type d -exec chmod 774 {} +
find $PWD -type f -exec chmod 664 {} +
```

- Set executables

``` shell
chmod 774 ./discord_stu/discord_stu.py
chmod 774 ./bin/service/install.sh
chmod 774 ./bin/service/uninstall.sh
```

## Installation Steps

- Create and complete configuration files

```shell
cp etc/config/discord_stu.config.json.example etc/config/discord_stu.config.json
```

- Install service

```shell
./bin/service/install.sh
```