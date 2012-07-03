#!/usr/bin/env python
# encoding: utf-8
"""
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
"""

from cStringIO import StringIO

import config

RED = "\033[31m{}\033[0m"
GREEN = "\033[32m{}\033[0m"
YELLOW = "\033[33m{}\033[0m"


class Command(object):
    def __init__(self, name, table_name):
        self.name = name
        self.table_name = table_name
        self.params = None

    def display(self, schema, db_schema):
        """
        None = db.schema == current.schema
            The database table matches the current schema so nothing to do

        sync = db.schema != current.schema && db.schema == migration.schema
            The database table does not match the current schema
            The database table matches what the migration_table is reporting

        force = db.schema != current.schema && db.schema != migration.schema
            The database table does not match the current schema
            The database table does not match what the changelog table is
            reporting
        """

        if self.name == 'create_table':
            if self.table_name in db_schema.tables:
                table = db_schema.tables[self.table_name]
                print(table)
                _sync = "[force]"
                _format_str = RED
            else:
                _sync = "[sync]"
                _format_str = YELLOW

        s = "{:7} {:13} {:20}".format(_sync, "new table:", "migrations")
        return "{}".format(_format_str.format(s))

    def get_yaml(self):
        s = StringIO()

        s.write('%s: ' % self.name)
        s.write('~')

        return_str = s.getvalue()
        s.close()
        return return_str


class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


class Changeset(object):
    def __init__(self):
        self.from_version = None
        self.to_version = None
        self.tables = AutoVivification()

    def __repr__(self):
        return self.get_yaml()

    def create_table(self, table):
        self.add(table.name, "create_table")
        self.tables[table.name].append(Command("create_table"))

    def load_from_dict(self, d):
        self.tables = AutoVivification()
        for table_name in d["tables"]:
            for command in d["tables"][table_name]:
                if (type(command) is str):
                    self.add(table_name, command)
                else:
                    for command_name in command.keys():
                        self.add(table_name, command_name,
                                 command[command_name])

    def add(self, table_name, command_name, params=None):
        cmd = Command(command_name, table_name)
        cmd.params = params
        self.tables[table_name][command_name] = cmd

    def get_yaml(self, indent=""):
        s = StringIO()
        s.write("%schangeset: \n" % indent)
        s.write("%s%stables: " % (indent, config.indent))
        if (not self.tables):
            s.write("~\n")
        else:
            s.write("\n")
            for table_name in self.tables:
                s.write('%s%s%s:\n' % (indent, config.indent * 2, table_name))
                for command in self.tables[table_name]:
                    s.write('%s%s' % (indent, config.indent * 3))
                    s.write(command.get_yaml())
                    s.write('\n')

        return_str = s.getvalue()
        s.close()
        return return_str


def main():
    pass

if __name__ == '__main__':
    main()
