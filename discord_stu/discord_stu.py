#!/usr/bin/env python3
# Import pips
import argparse
import datetime
import discord
from discord.ext import commands
import io
import json
import jsonschema
import logging
import markovify
import os
import random
import re
import signal
import sys
import time

# Import modules
import library

# Module constants
MODULE                = f'discord_stu'
DIR_BASE              = os.path.abspath(os.path.dirname(sys.path[0]))
DIR_ETC               = f'{DIR_BASE}/etc'
DIR_ETC_CONFIG        = f'{DIR_ETC}/config'
DIR_ETC_TEMPLATE      = f'{DIR_ETC}/template'
DIR_ETC_TRANSLATION   = f'{DIR_ETC}/translation'
DIR_ETC_VALIDATION    = f'{DIR_ETC}/validation'
DIR_VAR               = f'{DIR_BASE}/var'
DIR_VAR_CACHE         = f'{DIR_VAR}/cache'
DIR_VAR_LOG           = f'{DIR_VAR}/log'
DIR_VAR_PID           = f'{DIR_VAR}/pid'
DIR_VAR_SPOOL         = f'{DIR_VAR}/spool'
DIR_VAR_SPOOL_READY   = f'{DIR_VAR_SPOOL}/ready'
DIR_VAR_SPOOL_ARCHIVE = f'{DIR_VAR_SPOOL}/archive'
DIR_VAR_SPOOL_ERROR   = f'{DIR_VAR_SPOOL}/error'
PATH_MODULE_CONFIG    = f'{DIR_ETC_CONFIG}/{MODULE}.json'
PATH_MODULE_LOG       = f'{DIR_VAR_LOG}/{MODULE}.log'
PATH_MODULE_PID       = f'{DIR_VAR_PID}/{MODULE}.pid'

def signal_reload_config(signal_number: int, stack_frame: object):
    """Reloads app configuration on SIGHUP signal

    Args:
    signal_number (int): The signal number provided by the signal handler
    stack_frame (object): The current stack_frame at time of signal capture
    """
    logger.debug(f'function start: {sys._getframe(  ).f_code.co_name}')
    logger.info(f'{MODULE} Service received signal {signal.Signals(signal_number).name}')
    logger.info(f'Reloading configuration')
    try:
        global app_config
        app_config = library.load_config(PATH_MODULE_CONFIG)
    except OSError as error:
        logger.critical(f'Unable to open/read config: {PATH_MODULE_CONFIG}')
        sys.exit(1)
    except json.decoder.JSONDecodeError as error:
        logger.critical(f'Schema Decode Failed: {error}')
        sys.exit(1)
    except Exception as error:
        logger.exception(f'Unhandled Exception Occurred: {error}')
        sys.exit(1)

def signal_graceful_exit(signal_number: int, stack_frame: object):
    """Graceful exit of app on SIG* signal

    Ideal cleanup involves removing the PID file.

    Args:
    signal_number (int): The signal number provided by the signal handler
    stack_frame (object): The current stack_frame at time of signal capture
    """
    logger.debug(f'function start: {sys._getframe(  ).f_code.co_name}')
    logger.info(f'{MODULE} Service received signal {signal.Signals(signal_number).name}')
    try:
        library.pid_cleanup(PATH_MODULE_PID)
    except OSError as error:
        logger.critical(f'Unable to open/read pid file for pid cleanup: {PATH_MODULE_PID}')
        sys.exit(1)
    logger.info(f'{MODULE} Service has shutdown.')
    sys.exit(1)

def bot(discord_token, discord_guild):
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix='!',intents=intents)

    # Connection Event
    @bot.event
    async def on_ready():
        guild = discord.utils.get(bot.guilds, name=discord_guild)
        logger.info(f'{bot.user} connected to {guild.name}(id: {guild.id})')
        await bot.change_presence(activity=discord.Game(name='Human Simulator 2000'))

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this command.')

    @bot.command(name='speak')
    @commands.has_role('developers/gods')
    async def speak(ctx):
        response = 'Uh... *WOOF*'
        await ctx.send(response)

    # Message Watcher
    @bot.listen('on_message')
    async def whatever_you_want_to_call_it(message):
        if message.author == bot.user:
            return

        if 'Open the pod bay doors' in message.content:
            response = f'Discord Stu, cannot do.'
            await message.channel.send(response)

    bot.run(discord_token)

def main():
    logger.debug(f'function start: {sys._getframe(  ).f_code.co_name}')

    # Initialise validation
    try:
        logger.debug(f'load validation')
        validation = library.load_validation(DIR_ETC_VALIDATION, f'{MODULE}.*')
    except OSError:
        logger.critical(f'Unable to open/read dir: {DIR_ETC_VALIDATION}')
        sys.exit(1)
    except json.decoder.JSONDecodeError as error:
        logger.critical(f'Schema Decode Failed: {error}')
        sys.exit(1)
    except Exception as error:
        logger.exception(f'Unhandled Exception Occurred: {error}')
        sys.exit(1)

    # Initialise configuration
    try:
        logger.debug(f'load config')
        app_config = library.load_config(PATH_MODULE_CONFIG)
    except OSError as error:
        logger.critical(f'Unable to open/read config: {PATH_MODULE_CONFIG}')
        sys.exit(1)
    except json.decoder.JSONDecodeError as error:
        logger.critical(f'Schema Decode Failed: {error}')
        sys.exit(1)
    except Exception as error:
        logger.exception(f'Unhandled Exception Occurred: {error}')
        sys.exit(1)

    # Validate configuration
    try:
        logger.debug(f'validate loaded data')
        jsonschema.validate(instance=app_config, schema=validation[f'{MODULE}.config.json'])
    except (jsonschema.exceptions.SchemaError, jsonschema.exceptions.ValidationError) as error:
        logger.critical(f'Validation failed: {error.message}')
        logger.critical(f'Failed validating {error.validator} in {error._word_for_schema_in_error_message}{list(error.relative_schema_path)[:-1]}')
        logger.critical(f'    {error.schema}')
        logger.critical(f'On {error._word_for_instance_in_error_message} {list(error.relative_path)}')
        logger.critical(f'    "{error.instance}"')
        sys.exit(1)
    except Exception as error:
        logger.exception(f'Unhandled Exception Occurred: {error}')
        sys.exit(1)

    # Check for already running process to prevent clash
    try:
        logger.debug(f'Check for existing PID')
        existing_pid = library.pid_read(PATH_MODULE_PID)
    except OSError:
        logger.debug(f'No existing PID recorded: {PATH_MODULE_PID}')
        existing_pid = None
    except Exception as error:
        logger.exception(f'Unhandled Exception Occurred: {error}')
        sys.exit(1)

    # If there's a PID do health check
    if existing_pid:
        try:
            os.kill(int(existing_pid), 0)
        except OSError:
            logger.debug(f'PID {existing_pid} provided no response, assuming its dead.')
        else:
            logger.info(f'{MODULE} is already running under PID {existing_pid}')
            logger.info(f'Exiting this execution')
            sys.exit(1)

    # Record current PID
    try:
        logger.debug(f'Writeout current PID')
        library.pid_write(PATH_MODULE_PID)
    except OSError:
        logger.critical(f'Unable to open/read path: {PATH_MODULE_PID}')
        sys.exit(1)
    except Exception as error:
        logger.exception(f'Unhandled Exception Occurred: {error}')
        sys.exit(1)

    discord_token = app_config['discord_token']
    discord_guild = app_config['discord_guild']
    bot(discord_token, discord_guild)

if __name__ == '__main__':
    logger = library.logger_init(MODULE, PATH_MODULE_LOG)
    logger.info(f'Starting {MODULE}')

    # https://unix.stackexchange.com/questions/317492/list-of-kill-signals
    # 1) SIGHUP  - Reload requested
    # 2) SIGINT  - User Terminal kill (Ctrl+C)
    # 3) SIGQUIT - User Terminal kill (Ctrl+\)
    # ...
    # 9) SIGKILL - Immediate Termination (Straight up PID murder, this is uncatchable hence no handler)
    # ...
    # 15) SIGTERM - Casual Termination (End whenever you're done)
    #
    # Register handler for reload of configuration
    signal.signal(signal.SIGHUP, signal_reload_config)
    # Register handlers to enable graceful shutdown of service
    signal.signal(signal.SIGINT, signal_graceful_exit)
    signal.signal(signal.SIGQUIT, signal_graceful_exit)
    signal.signal(signal.SIGTERM, signal_graceful_exit)

    main()