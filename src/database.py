#!/usr/bin/env python
# encoding: utf-8
"""
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
"""

import errors


def get(connection_info):
    vendor = connection_info["vendor"]
    if (vendor == "mysql"):
        import db_mysql
        return db_mysql.Database(connection_info)
    else:
        raise errors.AppError('%s not supported.' % vendor)


##############################################################################
# DatabaseVersion
##############################################################################

class Database(object):
    def __init__(self):
        pass


##############################################################################
# DatabaseVersion
##############################################################################

class DatabaseVersion(object):
    def __init__(self):
        self.name = None
        self._expected_schema = None
        self._actual_schema = None
        self._is_syncable = None

    @property
    def is_syncable(self):
        return self._is_syncable

    @property
    def actual_schema(self):
        return self._actual_schema

    @actual_schema.setter
    def actual_schema(self, value):
        self._actual_schema = value
        self.__set_syncable()

    @property
    def expected_schema(self):
        return self._expected_schema

    @expected_schema.setter
    def expected_schema(self, value):
        self._expected_schema = value
        self.__set_syncable()

    def __set_syncable(self):
        self._is_syncable = self._expected_schema == None or self._actual_schema == self._expected_schema


def main():
    pass

if __name__ == '__main__':
    main()
