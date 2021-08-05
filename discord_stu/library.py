#!/usr/bin/env python3
# Import pips
import json
import logging
import os
import re


def load_config(path):
    with open(path, mode='r', encoding='utf-8', newline="\n") as f:
        config = json.load(f)
        return config


def load_validation(dir, pattern):
    validation = {}
    with os.scandir(dir) as files:
        for entry in files:
            if entry.is_file():
                if re.match(pattern, entry.name):
                    validation[f'{entry.name}'] = load_config(entry.path)
    return validation


class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        '''
        Format an exception so that it prints on a single line.

        Source: https://docs.python.org/3/howto/logging-cookbook.html#customized-exception-formatting
        '''
        result = super(OneLineExceptionFormatter, self).formatException(exc_info)
        return repr(result)

    def format(self, record):
        s = super(OneLineExceptionFormatter, self).format(record)
        if record.exc_text:
            s = s.replace('\n', '')
        return s


def logger_init(name, file):
    # formatter = OneLineExceptionFormatter('%(asctime)s|%(name)s|%(levelname)s|%(message)s')
    formatter = OneLineExceptionFormatter('%(asctime)s|%(name)s|%(process)d|%(levelname)s|%(message)s')
    log_handler_console = logging.StreamHandler()
    log_handler_console.setLevel(logging.INFO)
    log_handler_console.setFormatter(formatter)

    log_handler_file = logging.FileHandler(file)
    log_handler_file.setLevel(logging.DEBUG)
    log_handler_file.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(log_handler_console)
    logger.addHandler(log_handler_file)

    logger.debug('Logging initialised')

    return logger


def pid_cleanup(path):
    os.remove(path)


def pid_read(path):
    existing_pid = None
    with open(path, 'r') as reader:
        existing_pid = reader.read()
    return existing_pid


def pid_write(path):
    with open(path, 'w') as writer:
        writer.write(str(os.getpid()))