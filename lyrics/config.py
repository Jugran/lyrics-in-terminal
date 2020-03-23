#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from configparser import ConfigParser

import curses
import os

KEYS={
    'arrow_up': curses.KEY_UP,
    'arrow_down': curses.KEY_DOWN,
    'arrow_left': curses.KEY_LEFT,
    'arrow_right': curses.KEY_RIGHT
}

CONFIG_PATH = os.path.abspath(os.path.dirname(__file__))

class Config:
    def __init__(self, section):
        self.dict = {}

        self.filepath = os.path.join(CONFIG_PATH, 'lyrics.cfg')
        self.section = section

        self.load()
        self.set_constants()

    def __setitem__(self, key, value):
        self.dict[key] = value

    def __getitem__(self, key):
        return self.dict[key]

    def __contains__(self, key):
        return key in self.dict
  
    def __repr__(self):
        return self.dict.__repr__()

    def items(self):
        return [(k, v) for k,v in self.dict.items()]

    def load(self):
        try:
            config = ConfigParser()
            config.read(self.filepath)
        except Exception as e:
            pass
            # use default config

        conf = dict(config.items(self.section))
        assert isinstance(conf, dict)

        self.dict = conf

    def set_constants(self):
        for key, value in self.dict.items():
            if value in KEYS.keys():
                self.dict[key] = KEYS[value]
            else:
                try:
                    value = int(value)
                    self.dict[key] = value
                except ValueError:
                    # not integer
                    # change to ascii
                    if len(value) == 1:
                        self.dict[key] = ord(value)
    '''
    def save(self):
        config = ConfigParser()
        config.read(self.filepath)
        config[self.section] = self.dict

        with open(self.filepath, 'w') as file:
            config.write(file)
    '''
