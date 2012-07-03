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

import changeset

##############################################################################
# public functions
##############################################################################

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


def load_schema_from_file(filename):
    with file(filename, 'r') as stream:
        data = yaml.load(stream)
        s = Schema()
        s.load_from_dict(data)
        return s


def save_to_path(schema):
    for table in schema.tables:
        #filename = _PROJECT_PATH + "/schema/tables/"
        print(table)


##############################################################################
# Versions
##############################################################################


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


##############################################################################
# Version
##############################################################################


class Version(object):
    def __init__(self):
        self.name = None
        self._schema = Schema()
        self._changes = changeset.Changeset()
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
            _write_string(s, "version", self.name)
            if (self.hashcode):
                s.write("\nhash: %s\n" % self.hashcode)
            if (self.schema):
                s.write("%s" % repr(self.schema))
            return s.getvalue().rstrip()

    def load_from_dict(self, data):
        if "version" in data:
            self.name = data["version"]
        self._schema.load_from_dict(data)

    def remove_table(self, name):
        self.schema.remove_table(name)
        print("remove table in changelog")

    def add_table(self, table):
        self.schema.add_table(table)
        print("!!add table in changelog")


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

##############################################################################
# Schema
##############################################################################


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
                for name in self.tables:
                    table = self.tables[name]
                    s.write(indent(repr(table), is_list=True))
                    s.write("\n")
            else:
                s.write(" ~\n")
            return s.getvalue().strip()

    def clear(self):
        self.tables = {}

    def save_to_path(self, path):
        for table_name in self.tables:
            table = self.tables[table_name]
            print(table)
            #print(table)

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


##############################################################################
# Table
##############################################################################


class Table(object):
    def __init__(self):
        self.name = None
        self.columns = []

    def load_from_file(self, filename):
        with file(filename, 'r') as stream:
            data = yaml.load(stream)
            self.load_from_dict(data)

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


##############################################################################
# Column
##############################################################################


class Column(object):
    def __init__(self):
        self.name = None
        self.type = None
        self.default = None
        self.nullable = True
        self.key = False
        self.autoincrement = False

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
            s.write('name: %s\n' % self.name)
            s.write('type: %s\n' % self.type)

            _write_bool(s, "key", self.key)
            _write_bool(s, "nullable", self.nullable)
            if (self.default):
                s.write('default: "%s"\n' % self.default)

            return s.getvalue()


##############################################################################
# Procedure
##############################################################################


class Procedure(object):
    def __init__(self):
        pass


##############################################################################
# Parameter
##############################################################################


class Parameter(object):
    def __init__(self):
        pass


##############################################################################
# Changelog
##############################################################################


class Changelog(object):
    def __init__(self):
        self.from_version = None
        self.to_version = None


##############################################################################
# Helper functions
##############################################################################

def _write_bool(s, name, value):
    if (value):
        s.write('%s: true\n' % name)
    else:
        s.write('%s: false\n' % name)


def _write_string(s, name, value):
    if (value):
        s.write("%s: %s" % (name, value))
    else:
        s.write("%s: ~" % name)


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
    return "".join(newlist)


def caseinsensitive_sort(stringList):
    """case-insensitive string comparison sort
    doesn't do locale-specific compare
    though that would be a nice addition
    usage: stringList = caseinsensitive_sort(stringList)"""

    tupleList = [(x.lower(), x) for x in stringList]
    tupleList.sort()
    return [x[1] for x in tupleList]


def main():
    pass

if __name__ == '__main__':
    main()
