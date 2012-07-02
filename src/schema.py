#!/usr/bin/env python
# encoding: utf-8
"""
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
"""

import glob
import hashlib
import os
import re
import yaml
from cStringIO import StringIO
from contextlib import closing

import config


##############################################################################
# public functions
##############################################################################

_path = os.path.abspath(".")
def get_versions():
    filename = _path + "/versions/index.yml"
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
        for filename in glob.glob(_path + "/schema/*.yml"):
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
            s.write("version: %s" % self.name)
            if (self.hashcode):
                s.write("\nhash: %s\n" % self.hashcode)
            if (self.schema):
                s.write("\n%s" % repr(self.schema))
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
        print("add table in changelog")




class VersionFile(Version):
    def __init__(self):
        super(VersionFile, self).__init__()
        self.filename = None


    def load(self):
        with file(_path + "/versions/" + self.filename, 'r') as stream:
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
                    s.write(_indent(repr(table)))
                    s.write("\n")
            else:
                s.write(" ~\n")
            return s.getvalue()


    def clear(self):
        self.tables = {}


    def load_from_dict(self, data):
        assert "tables" in data, "expecting tables key in dictionary"

        tables = data["tables"]
        if tables:
            for name in tables:
                table = Table()
                table.name = name
                table.load_from_dict(tables[name])
                self.tables[table.name] = table

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


    def load_from_dict(self, data):
        assert "columns" in data, "'columns' key must exist in table dictionary"

        self.columns = [] # Reset the columns list to empty

        # columns
        columns = data["columns"]
        for d in columns:
            column = Column()
            column.load_from_dict(d)
            self.columns.append(column)

        # constraints


    def __repr__(self):
        with closing(StringIO()) as s:
            s.write("%s:\n" % self.name)
            s.write(_indent("columns:\n"))
            for column in self.columns:
                s.write(_indent(repr(column), 2))
            return s.getvalue()




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
        assert len(data) == 1, "Expecting one element in the column dictionary"
        assert "type" in data.items()[0][1]

        item = data.items()[0]
        self.name = item[0]
        self.key = item[1]["key"] if "key" in item[1] else False
        self.type = item[1]["type"]
        self.default = item[1]["default"] if "default" in item[1] else None
        self.nullable = item[1]["nullable"] if "nullable" in item[1] else None


    def __repr__(self):
        with closing(StringIO()) as s:
            s.write("- %s:\n" % self.name)
            s.write(_indent("type: %s\n" % self.type))

            if (self.key):
                s.write(_indent("key: true\n"))
            if (self.default):
                s.write(_indent("default: %s\n" % self.default))
            if (self.nullable):
                s.write(_indent("nullable: %s\n" % self.nullable))

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

_compiled_re = re.compile('^(?P<all>.*)$', re.MULTILINE)
def _indent(strings, indent=1):

    #print('before: [%s]' % strings)
    newstr = _compiled_re.sub(config.indent * indent + '\g<all>', strings.rstrip())
    if strings[-1] == "\n":
        newstr = newstr + "\n"

    #print('after: [%s]' % newstr)
    return newstr




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

