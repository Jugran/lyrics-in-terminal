#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lyrics import CONFIG_PATH
from configparser import ConfigParser

import curses

KEYS={
    'arrow_up': curses.KEY_UP,
    'arrow_down': curses.KEY_DOWN,
    'arrow_left': curses.KEY_LEFT,
    'arrow_right': curses.KEY_RIGHT
}

class Config:
    def __init__(self, section):
        """
        Load configuration from configuration file.

        Args:
            self: (todo): write your description
            section: (todo): write your description
        """
        self.dict = {}

        self.filepath = CONFIG_PATH
        self.section = section

        self.load()
        self.set_constants()

    def __setitem__(self, key, value):
        """
        Sets the value of a key.

        Args:
            self: (todo): write your description
            key: (str): write your description
            value: (str): write your description
        """
        self.dict[key] = value

    def __getitem__(self, key):
        """
        Return the value of a dictionary.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        return self.dict[key]

    def __contains__(self, key):
        """
        Determine if key contains a value.

        Args:
            self: (todo): write your description
            key: (todo): write your description
        """
        return key in self.dict
  
    def __repr__(self):
        """
        Return a repr representation of this object.

        Args:
            self: (todo): write your description
        """
        return self.dict.__repr__()

    def items(self):
        """
        Return a copy of this collection items.

        Args:
            self: (todo): write your description
        """
        return [(k, v) for k,v in self.dict.items()]

    def load(self):
        """
        Load config file.

        Args:
            self: (todo): write your description
        """
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
        """
        Set constant constants.

        Args:
            self: (todo): write your description
        """
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
