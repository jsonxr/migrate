#!/usr/bin/env python
# encoding: utf-8
"""
Created by Jason Rowland on 2012-05-25.
Copyright (c) 2012 Jason Rowland. All rights reserved.
"""

import sys

indent = "    "
changelog = 'changelog'


def load(yml):
    if (yml and 'settings' in yml):
        global changelog
        changelog = yml['settings']['changelog']

        global indent
        i = yml['settings']['indent']
        if (i > 0):
            indent = " " * i


def main(argv=None):
    pass

if __name__ == "__main__":
    sys.exit(main())
