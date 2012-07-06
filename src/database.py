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
        self.expected_schema = None
        self.actual_schema = None


def main():
    pass

if __name__ == '__main__':
    main()
