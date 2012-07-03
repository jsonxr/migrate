#!/usr/bin/env python
# encoding: utf-8
"""
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
"""

import glob
import hashlib
import os
import yaml
from cStringIO import StringIO
from contextlib import closing

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
                    version = VersionFile()
                    version.name = name
                    version.filename = v[name]
                    versions.append(version)
        return versions
    except IOError, e:
        if e.errno == 2 and e.strerror == "No such file or directory":
            return None
        else:
            raise e


def create_bootstrap(schema):
    b = VersionFile()
    b.name = 'bootstrap'
    b.filename = 'bootstrap.yml'
    b.schema = schema
    b.save()
    return b


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
        v = VersionFile()
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

    @property
    def hashcode(self):
        return self._schema.hashcode

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, value):
        self._schema = value

    def __eq__(self, other):
        return (repr(self) == repr(other))

    def __repr__(self):
        with closing(StringIO()) as s:
            _write_string(s, "version: %s", self.name)
            if (self.hashcode):
                s.write("\nhash: %s\n" % self.hashcode)
            if (self.schema):
                s.write(repr(self.schema))
            if (self.migration):
                s.write("\nmigration:")
                s.write("\n" + indent(repr(self.migration)))
            else:
                s.write("\nmigration: ~")
            return s.getvalue().rstrip()

    def load_from_dict(self, data):
        if "version" in data:
            self.name = data["version"]
        self._schema.load_from_dict(data)
        self.migration = Migration()
        if "migration" in data:
            self.migration.load_from_dict(data["migration"])

    def drop_table(self, name):
        self.schema.remove_table(name)
        self.migration.add_command(Command(name, 'drop_table'))

    def create_table(self, table):
        self.schema.add_table(table)
        self.migration.add_command(Command(table.name, 'create_table'))


#=============================================================================
# VersionFile
#=============================================================================

class VersionFile(Version):
    def __init__(self):
        super(VersionFile, self).__init__()
        self.filename = None

    def load(self):
        with file(_PROJECT_PATH + "/versions/" + self.filename, 'r') as stream:
            data = yaml.load(stream)
            self.load_from_dict(data)

    def save(self):
        with file('versions/%s' % self.filename, 'w') as f:
            f.write(repr(self))


#=============================================================================
# Schema
#=============================================================================

class Schema(object):
    def __init__(self):
        self.tables = {}

    def __eq__(self, other):
        return (repr(self) == repr(other))

    def __repr__(self):
        with closing(StringIO()) as s:
            s.write("tables:")
            if (self.tables):
                s.write("\n")

                names = sorted(self.tables, key=str.lower)
                for name in names:
                    table = self.tables[name]
                    s.write(indent(repr(table), is_list=True))
                    s.write("\n")
            else:
                s.write(" ~\n")
            return s.getvalue().strip()

    def clear(self):
        self.tables = {}

    def load_from_path(self, path):
        self.clear()
        # Tables
        for filename in glob.glob(os.path.join(path, 'tables/*.yml')):
            t = Table()
            t.load_from_file(filename)
            self.add_table(t)

    def save_to_path(self, path):
        # Tables
        if not os.path.exists(path + "/tables"):
            os.mkdir(path + "/tables")
        for table_name in self.tables:
            table = self.tables[table_name]
            filename = "%s/tables/%s.yml" % (path, table.name)
            table.save_to_file(filename)
        # Procedures

    def load_from_dict(self, data):
        assert "tables" in data, "expecting tables key in dictionary"

        tables = data["tables"]
        if tables:
            for d in tables:
                table = Table()
                table.load_from_dict(d)
                self.add_table(table)

    @property
    def hashcode(self):
        m = hashlib.sha1()
        m.update(repr(self))
        return m.hexdigest()

    def remove_table(self, name):
        del self.tables[name]

    def add_table(self, table):
        self.tables[table.name] = table


#=============================================================================
# Table
#=============================================================================

class Table(object):
    def __init__(self, name=None):
        self.name = name
        self.columns = []

    def load_from_file(self, filename):
        with file(filename, 'r') as stream:
            data = yaml.load(stream)
            self.load_from_dict(data)

    def save_to_file(self, filename):
        with file(filename, 'w') as stream:
            stream.write(repr(self))

    def load_from_dict(self, data):
        assert "columns" in data

        self.name = data["name"]
        self.columns = []  # Reset the columns list to empty

        # columns
        columns = data["columns"]
        for d in columns:
            column = Column()
            column.load_from_dict(d)
            self.columns.append(column)

        # constraints

    def add_column(self, name, col_type):
        column = Column()
        column.name = name
        column.type = col_type
        self.columns.append(column)
        return column

    def __repr__(self):
        with closing(StringIO()) as s:
            s.write("name: %s\n" % self.name)
            s.write("columns:\n")
            for column in self.columns:
                s.write(indent(repr(column), is_list=True) + "\n")
            return s.getvalue().strip()


#=============================================================================
# Column
#=============================================================================

class Column(object):
    def __init__(self, name=None, col_type=None, default=None, nullable=True, key=False, autoincrement=False):
        self.name = name
        self.type = col_type
        self.default = default
        self.nullable = nullable
        self.key = key
        self.autoincrement = autoincrement

    def load_from_dict(self, data):
        assert "name" in data
        assert "type" in data

        self.name = data["name"]
        self.type = data["type"]
        self.key = data["key"] if "key" in data else False
        self.default = data["default"] if "default" in data else None
        self.nullable = data["nullable"] if "nullable" in data else True

    def __repr__(self):
        with closing(StringIO()) as s:
            s.write('{ ')
            s.write('name: "%s"' % self.name)
            s.write(', type: "%s"' % self.type)
            _write_bool(s, ", key: %s", self.key)
            _write_bool(s, ", nullable: %s", self.nullable)
            if (self.default):
                s.write(', default: "%s"' % self.default)
            s.write(' }')
            return s.getvalue()


#=============================================================================
# Procedure
#=============================================================================

class Procedure(object):
    def __init__(self):
        pass


#=============================================================================
# Parameter
#=============================================================================

class Parameter(object):
    def __init__(self):
        pass


#=============================================================================
# Migration
#=============================================================================

class Migration(object):
    def __init__(self, previous=None):
        self.previous = previous
        self.commands = []

    def __repr__(self):
        with closing(StringIO()) as s:
            _write_string(s, "previous: %s\n", self.previous)
            if self.commands:
                s.write("commands:\n")
                sorted_commands = sorted(self.commands,
                                         key=lambda c: ("%s %s %s" % (c.table, c.name, c.column)).lower())
                for c in sorted_commands:
                    s.write(indent(repr(c) + "\n", is_list=True))
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

    def add_command(self, command):
        self.commands.append(command)


#=============================================================================
# Command
#=============================================================================

class Command(object):
    def __init__(self, table=None, name=None, old=None, column=None):
        self.name = name
        self.table = table
        self.old = old
        self.column = column

    def __repr__(self):
        with closing(StringIO()) as s:
            s.write("{ ")
            s.write("table: %s" % self.table)
            s.write(", name: %s" % self.name)
            if self.column:
                s.write(", column: %s" % self.column)
            if self.old:
                s.write(", old: %s" % self.old)
            s.write(" }")
            return s.getvalue().strip()

    def load_from_dict(self, data):
        self.name = data["name"]
        self.table = data["table"]
        self.old = data["old"] if "old" in data else None
        self.column = data["column"] if "column" in data else None


#=============================================================================
# Helper functions
#=============================================================================

def _write_bool(s, string, value):
    if (value):
        s.write(string % 'true')
    else:
        s.write(string % 'false')


def _write_string(s, string, value):
    if (value):
        s.write(string % value)
    else:
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
