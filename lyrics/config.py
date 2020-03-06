#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from configparser import ConfigParser
import curses

KEYS={
    'arrow_up': curses.KEY_UP,
    'arrow_down': curses.KEY_DOWN,
    'arrow_left': curses.KEY_LEFT,
    'arrow_right': curses.KEY_RIGHT
}

class Config(dict):
    def __init__(self, section):
        # super().__init__()
        filepath = 'lyrics.cfg'

        config = self.load_config(filepath)[section]
        for key, value in config.items():
            self.__setitem__(key, value)

        # self.__dict__ = super().__dict__
        set_constants(self)

    # def __contains__(self, key):
    #     return super().__contains__(key)
  
    def __getitem__(self, key):
        return super().__getitem__(key)
  
    def __setitem__(self, key, value):
        return super().__setitem__(key, value)

    def __repr__(self):
        return super().__repr__()

    def items(self):
        return [(k, v) for k,v in super().items()]

    def load_config(self, filepath):
        try:
            config = ConfigParser()
            config.read(filepath)
        except Exception as e:
            pass
            # use default config

        conf = {section: dict(config.items(section)) for section in config.sections()}

        return conf

def set_constants(config):
    for key, value in config.items():
        if value in KEYS.keys():
            config[key] = KEYS[value]
        else:
            try:
                value = int(value)
                config[key] = value
            except ValueError:
                continue
