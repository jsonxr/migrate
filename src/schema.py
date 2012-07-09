#!/usr/bin/env python
# encoding: utf-8
"""
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
"""

import glob
import os
import yaml
from cStringIO import StringIO
from contextlib import closing

import errors

#=============================================================================
# public functions
#=============================================================================

_PROJECT_PATH = os.path.abspath(".")


def get_versions():
    filename = _PROJECT_PATH + "/versions/index.yml"
    try:
        versions = Versions()
        with file(filename, 'r') as stream:
            data = yaml.load(stream)
            if data:
                for v in data:
                    name = v.keys()[0]
                    version = Version()
                    version.name = name
                    version.filename = v[name]
                    versions.append(version)
        return versions
    except IOError, e:
        if e.errno == 2 and e.strerror == "No such file or directory":
            return None
        else:
            raise e


#=============================================================================
# Columns
#=============================================================================

class Columns(list):

    def __getattr__(self, name):
        for c in self:
            if c.name == name:
                return c
        raise KeyError(name)


#=============================================================================
# Column
#=============================================================================

class Column(object):
    NULLABLE_DEFAULT = True
    KEY_DEFAULT = False
    AUTOINCREMENT_DEFAULT = False

    def __init__(self, name=None, col_type=None, default=None,
                 nullable=NULLABLE_DEFAULT, key=KEY_DEFAULT, autoincrement=AUTOINCREMENT_DEFAULT):
        self.name = name
        self.type = col_type
        self.key = key or Column.KEY_DEFAULT
        self.default = default
        self.nullable = nullable or Column.NULLABLE_DEFAULT
        self.autoincrement = autoincrement or Column.AUTOINCREMENT_DEFAULT

    def __eq__(self, other):
        result = (self.name == other.name
                  and self.type == other.type
                  and self.key == other.key
                  and self.default == other.default
                  and self.nullable == other.nullable
                  and self.autoincrement == other.autoincrement
                  )
        return result

    def __repr__(self):
        return "<column name='%s' type='%s'>" % (self.name, self.type)

    def load_from_dict(self, data):
        assert "name" in data
        assert "type" in data

        self.name = data["name"]
        self.type = data["type"]
        self.key = data["key"] if "key" in data else Column.KEY_DEFAULT
        self.default = data["default"] if "default" in data else None
        self.nullable = data["nullable"] if "nullable" in data else Column.NULLABLE_DEFAULT
        self.autoincrement = data["autoincrement"] if "autoincrement" in data else Column.AUTOINCREMENT_DEFAULT

    def get_yml(self, verbose=False):
        with closing(StringIO()) as s:
            s.write('{ ')
            _write_str(s, 'name: %s', self.name, verbose=True, quote=True)
            _write_str(s, ', type: %s', self.type, verbose=True, quote=True)
            _write_bool(s, ", key: %s", self.key, Column.KEY_DEFAULT, verbose=verbose)
            _write_str(s, ', default: %s', self.default, verbose=verbose, quote=True)
            _write_bool(s, ", nullable: %s", self.nullable, Column.NULLABLE_DEFAULT, verbose=verbose)
            _write_bool(s, ", autoincrement: %s", self.autoincrement, Column.AUTOINCREMENT_DEFAULT, verbose=verbose)
            s.write(' }')
            return s.getvalue()


#=============================================================================
# Table
#=============================================================================

class Table(object):
    def __init__(self, name=None):
        self.name = name
        self.columns = Columns()

    def __repr__(self):
        return "<table name='%s' cols=%s>" % (self.name, self.columns)

    def __eq__(self, other):
        if other == None:
            return False
        else:
            return self.name == other.name and self.columns == other.columns

    def clear(self):
        self.columns = Columns()

    def load_from_file(self, filename):
        self.clear()
        with file(filename, 'r') as stream:
            data = yaml.load(stream)
            self.load_from_dict(data)

    def save_to_file(self, filename, verbose=False):
        with file(filename, 'w') as stream:
            stream.write(self.get_yml(verbose))

    def load_from_dict(self, data):
        assert "columns" in data
        self.clear()  # Reset the columns list to empty
        self.name = data["name"]
        columns = data["columns"]
        for d in columns:
            column = Column()
            column.load_from_dict(d)
            self.columns.append(column)

        # constraints

    def add_column(self, name, col_type, default=None,
                 nullable=Column.NULLABLE_DEFAULT, key=Column.KEY_DEFAULT, autoincrement=Column.AUTOINCREMENT_DEFAULT):
        column = Column(name, col_type, default=default, nullable=nullable, key=key, autoincrement=autoincrement)
        #column.name = name
        #column.type = col_type
        self.columns.append(column)
        return column

    def get_yml(self, verbose=False):
        with closing(StringIO()) as s:
            _write_str(s, "name: %s\n", self.name, verbose=True)
            s.write("columns:\n")
            for column in self.columns:
                s.write(indent(column.get_yml(verbose), is_list=True) + "\n")
            return s.getvalue().strip()


#=============================================================================
# Tables
#=============================================================================

class Tables(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        assert value.name
        assert "columns" in value.__dict__
        if name == value.name:
            self[name] = value
        else:
            raise KeyError(name)

    def __eq__(self, other):
        if (other is None):
            return False
        else:
            equal = self.items() == other.items()
            return equal


#=============================================================================
# Parameter
#=============================================================================

class Parameter(object):
    def __init__(self):
        pass


#=============================================================================
# Procedure
#=============================================================================

class Procedure(object):
    def __init__(self):
        pass


#=============================================================================
# Command
#=============================================================================

class Command(object):

    valid_commands = ['create_table', 'drop_table', 'rename_table',  # table commands
                      'add_column', 'remove_column', 'change_column', 'rename_column',  # column commands
                      'add_index', 'remove_index',
                      'sql']

    def __init__(self, table=None, name=None, old=None, column=None):
        self.name = name
        self.table = table
        self.old = old
        self.column = column
        self._validate()

    def get_yml(self, verbose=False):
        with closing(StringIO()) as s:
            s.write("{ ")
            _write_str(s, "table: %s", self.table, verbose=True, quote=True)
            _write_str(s, ", name: %s", self.name, verbose=True, quote=True)
            _write_str(s, ", column: %s", self.column, verbose=verbose, quote=True)
            _write_str(s, ", old: %s", self.old, verbose=verbose, quote=True)
            s.write(" }")
            return s.getvalue().strip()

    def load_from_dict(self, data):
        self.name = data["name"]
        self.table = data["table"]
        self.old = data["old"] if "old" in data else None
        self.column = data["column"] if "column" in data else None
        self._validate()

    def _validate(self):
        if not self.name is None and not self.name in Command.valid_commands:
            raise errors.AppError("%s is not a valid command" % self.name)


#=============================================================================
# Migration
#=============================================================================

class Migration(object):
    def __init__(self, previous=None):
        self.previous = previous
        self.commands = []

    def get_yml(self, verbose=False):
        with closing(StringIO()) as s:
            _write_str(s, "previous: %s\n", self.previous, True)
            if self.commands:
                s.write("commands:\n")
                sorted_commands = sorted(self.commands,
                                         key=lambda c: ("%s %s %s" % (c.table, c.name, c.column)).lower())
                for c in sorted_commands:
                    s.write(indent(c.get_yml(verbose) + "\n", is_list=True))
            else:
                s.write("commands: ~\n")

            return s.getvalue().strip()

    def clear(self):
        self.commands = []

    def load_from_dict(self, data):
        self.clear()
        self.previous = data["previous"] if "previous" in data else None
        for d in data["commands"]:
            command = Command()
            command.load_from_dict(d)
            self.add_command(command)

    def save_to_file(self, filename, verbose=False):
        with file(filename, 'w') as stream:
            stream.write(self.get_yml(verbose))

    def add_command(self, command):
        self.commands.append(command)


#=============================================================================
# Schema
#=============================================================================

class Schema(object):
    def __init__(self):
        self.tables = Tables()

    def __repr__(self):
        return "<schema tables=%s>" % self.tables

    def __eq__(self, other):
        if other is None:
            return False
        else:
            result = self.tables.items() == other.tables.items()
            return result

    def get_yml(self, verbose=False):
        with closing(StringIO()) as s:
            s.write("tables:")
            if (self.tables):
                s.write("\n")

                names = sorted(self.tables, key=str.lower)
                for name in names:
                    table = self.tables[name]
                    s.write(indent(table.get_yml(verbose), is_list=True))
                    s.write("\n")
            else:
                s.write(" ~\n")
            return s.getvalue().strip()

    def __nonzero__(self):
        if self.tables is None:
            return 0
        else:
            return len(self.tables)

    def __bool__(self):
        return self.__nonzero__() > 0

    def clear(self):
        self.tables = Tables

    def load_from_path(self, path):
        self.clear()
        # Tables
        for filename in glob.glob(os.path.join(path, 'tables/*.yml')):
            t = Table()
            t.load_from_file(filename)
            self.add_table(t)

    def load_from_str(self, string):
        data = yaml.load(string)
        self.load_from_dict(data)

    def load_from_dict(self, data):
        assert "tables" in data, "expecting tables key in dictionary"

        tables = data["tables"]
        if tables:
            for d in tables:
                table = Table()
                table.load_from_dict(d)
                self.add_table(table)

    def save_to_path(self, path, verbose=False):
        # Tables
        if not os.path.exists(path + "/tables"):
            os.mkdir(path + "/tables")
        for table_name in self.tables:
            table = self.tables[table_name]
            filename = "%s/tables/%s.yml" % (path, table.name)
            table.save_to_file(filename, verbose)
        # Procedures

    def remove_table(self, name):
        del self.tables[name]

    def add_table(self, table):
        assert table.name
        self.tables[table.name] = table


#=============================================================================
# Versions
#=============================================================================

class Versions(object):
    def __init__(self):
        self.versions = []

    def append(self, version):
        self.versions.append(version)

    def get_previous(self):
        if len(self.versions) >= 1:
            return self.versions[-1]
        else:
            return None

    def get_current(self):
        v = Version()
        v.name = "current"
        v.filename = "current.yml"
        return v

    def get_from_path(self):
        v = Version()
        v.name = "path"
        for filename in glob.glob(_PROJECT_PATH + "/schema/*.yml"):
            with file(filename, 'r') as stream:
                data = yaml.load(stream)
                v.load_from_dict(data)
        return v


#=============================================================================
# Version
#=============================================================================

class Version(object):
    def __init__(self):
        self.name = None
        self._schema = Schema()
        self.migration = Migration()
        self.syncable = False
        self.filename = None

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, value):
        self._schema = value

    def __eq__(self, other):
        return (self.get_yml(verbose=True) == other.get_yml(verbose=True))

    def get_yml(self, verbose=False):
        with closing(StringIO()) as s:
            _write_str(s, "version: %s\n", self.name, True)
            if (self.schema):
                s.write(self.schema.get_yml(verbose))
            if (self.migration):
                s.write("\nmigration:")
                s.write("\n" + indent(self.migration.get_yml(verbose)))
            else:
                s.write("\nmigration: ~")
            return s.getvalue().rstrip()

    def load_from_file(self, filename=None):
        if filename:
            self.filename = filename
        with file(filename, 'r') as stream:
            data = yaml.load(stream)
            self.load_from_dict(data)

    def load_from_dict(self, data):
        if "version" in data:
            self.name = data["version"]
        self._schema.load_from_dict(data)
        self.migration = Migration()
        if "migration" in data:
            self.migration.load_from_dict(data["migration"])

    def save_to_file(self, filename=None, verbose=True):
        if filename is None:
            filename = self.filename
        with file(filename, 'w') as f:
            f.write(self.get_yml(verbose))

    def save_to_path(self, path, verbose=False):
        os.makedirs(path)
        self.schema.save_to_path(path, verbose)
        self.migration.save_to_file(path + "/migration.yml", verbose)

    def drop_table(self, name):
        self.schema.remove_table(name)
        self.migration.add_command(Command(name, 'drop_table'))

    def create_table(self, table):
        self.schema.add_table(table)
        self.migration.add_command(Command(table.name, 'create_table'))


#=============================================================================
# Helper functions
#=============================================================================

def _write_bool(s, string, value, default, verbose=False):
    if verbose or value != default:
        if (value):
            s.write(string % 'true')
        else:
            s.write(string % 'false')


def _write_int(s, formatstr, value):
    if not value is None:
        s.write(formatstr % value)


def _write_str(s, string, value, verbose=False, write_if_empty=False, quote=False):
    if (value):
        if quote:
            s.write(string % '"' + value.replace('"', '\\"') + '"')
        else:
            s.write(string % value)
    else:
        if verbose or write_if_empty:
            s.write(string % "~")


def indent(value, indent=1, is_list=False):
    strings = value.rstrip().splitlines(True)

    first = "    " * indent
    others = "    " * indent
    if is_list:
        first += "- "
        others += "  "

    newlist = [first + strings[0]]
    for i in range(1, len(strings)):
        newlist.append(others + strings[i])

    newstr = "".join(newlist)
    if value[-1] == "\n":
        newstr += "\n"
    return newstr


#=============================================================================
# main
#=============================================================================

def main():
    pass

if __name__ == '__main__':
    main()
