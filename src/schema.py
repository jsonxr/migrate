#!/usr/bin/env python
# encoding: utf-8
"""
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
"""

import glob
import os
import re
import yaml
from cStringIO import StringIO
from contextlib import closing

import cache
from errors import AppError


#=============================================================================
# Columns
#=============================================================================

class Columns(list):
    def add(self, name, col_type, default=None, nullable=True, key=False, autoincrement=False):
        column = Column(name, col_type, default=default, nullable=nullable, key=key, autoincrement=autoincrement)
        self.append(column)

#    def __getstate__(self):
#        return self.__dict__
#
#    def __setstate__(self, d):
#        self.__dict__.update(d)
#    def __getattr__(self, name):
#        for c in self:
#            if c.name == name:
#                return c
#        raise KeyError(name)


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
            string = stream.read()
        self.load_from_str(string)

    def load_from_str(self, string):
        data = yaml.load(string)
        self.load_from_dict(data)

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

    def save_to_file(self, filename, verbose=False):
        with file(filename, 'w') as stream:
            stream.write(self.get_yml(verbose))

    def add_column(self, name, col_type, default=None,
                 nullable=Column.NULLABLE_DEFAULT, key=Column.KEY_DEFAULT, autoincrement=Column.AUTOINCREMENT_DEFAULT):
        column = Column(name, col_type, default=default, nullable=nullable, key=key, autoincrement=autoincrement)
        #column.name = name
        #column.type = col_type
        self.columns.append(column)
        return column

    def get_column(self, name):
        for col in self.columns:
            if col.name == name:
                return col
        return None

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

class Tables(object):
    def __init__(self):
        self.table_dict = {}

    def __repr__(self):
        return "<tables=%s>" % len(self.table_dict)

    def __str__(self):
        return self.__repr__()
#    def __getstate__(self):
#        return self.__dict__
#
#    def __setstate__(self, d):
#        self.__dict__.update(d)

    def __iter__(self):
        return self.table_dict.__iter__()

    def __getitem__(self, key):
        if key in self.table_dict:
            return self.table_dict.__getitem__(key)

    def __setitem__(self, key, value):
        self.table_dict.__setitem__(key, value)

    def __len__(self):
        return len(self.table_dict)

    def __eq__(self, other):
        if (other is None):
            return False
        else:
            equal = self.table_dict.items() == other.table_dict.items()
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
# Commands
#=============================================================================
#
#
#class Command(object):
#    actions = {}
#
#    def __init__(self):
#        self.params = {}
#
#    @staticmethod
#    def register(command):
#        Command.actions[command.action] = command
#
#    def get_yml(self, verbose=False):
#        with closing(StringIO()) as s:
#            _write_str(s, 'action: %s\n', self.action, verbose=True, quote=False)
#            if self.params:
#                s.write('params:\n')
#                s.write(indent(output_yaml(self.params, ['table', 'columns', 'renameto'])))
#            return s.getvalue().strip()
#
#    @staticmethod
#    def load_from_dict(data):
#        constructor = Command.actions[data['action']]
#        cmd = constructor()
#        cmd.params = data['params']
#        return cmd


class TableMigration(object):
    def __init__(self):
        self._table_name = None
        self._commands = {}

    def __repr__(self):
        action = None
        for cmd_name in self._commands:
            cmd = self._commands[cmd_name]
            if action:
                action += ',' + cmd.action
            else:
                action = cmd.action
        return "<TableMigration table=%s actions=%s>" % (self._table_name, action)

    @property
    def table_name(self):
        return self._table_name

    @table_name.setter
    def table_name(self, table_name):
        self._table_name = table_name

    @property
    def commands(self):
        return self._commands

    def get_yml(self, verbose=False):
        with closing(StringIO()) as s:
            _write_str(s, '%s:\n', self._table_name, verbose=True, quote=False)
            sorted_commands = sorted(self._commands.keys(), key=lambda c: c.lower())
            for key in sorted_commands:
                cmd = self._commands[key]
                s.write(indent(cmd.get_yml(verbose) + '\n'))
            return s.getvalue().strip()

    def load_from_dict(self, data):
        for action in data:
            constructor = TableCommand.actions[action]
            cmd = constructor()
            d = data[action]
            if d != None:
                cmd.load_from_dict(d)
            self._commands[action] = cmd
#
#    def create(self):
#        cmd = CreateTableCommand()
#        self.add_command(cmd)
#
#    def drop(self):
#        cmd = DropTableCommand()
#        self.add_command(cmd)
#
#    def rename(self, rename_from):
#        cmd = RenameTableCommand()
#        cmd.rename_from = rename_from
#        self.add_command(cmd)

    def add_command(self, cmd):
        self._commands[cmd.action] = cmd


class TableCommand(object):
    actions = {}

    @staticmethod
    def register(command):
        TableCommand.actions[command.action] = command

    def get_yml(self, verbose=False):
        return '%s: ~' % self.action


class CreateTableCommand(TableCommand):
    action = "create"
    display = "create table"
    sort_order = 2

    def __init__(self):
        self.table_name = None


class DropTableCommand(TableCommand):
    action = "drop"
    display = "drop table"
    sort_order = 4

    def __init__(self):
        self.table_name = None


class RenameTableCommand(TableCommand):
    action = "renamefrom"
    display = "rename table"
    sort_order = 1

    def __init__(self):
        self.table_name = None
        self.rename_from = None

    def __repr__(self):
        return "<rename_table renamefrom='%s'>" % self.rename_from

    def get_yml(self, verbose=False):
        return '%s: %s' % (self.action, self.rename_from)

    def load_from_dict(self, data):
        self.rename_from = data


class AlterTableCommand(TableCommand):
    action = "alter"
    display = "alter table"
    sort_order = 3

    def __init__(self):
        self.table_name = None
        self.columns = {}

    def add_command(self, cmd):
        self.columns[cmd.column_name] = cmd  # [cmd.column_name] = cmd

    def add(self, column_name):
        cmd = AddColumnCommand()
        cmd.column_name = column_name
        self.add_command(cmd)

    def rename(self, column_name, rename_from):
        cmd = RenameColumnCommand()
        cmd.column_name = column_name
        cmd.rename_from = rename_from
        self.add_command(cmd)

    def remove(self, column_name):
        cmd = RemoveColumnCommand()
        cmd.column_name = column_name
        self.add_command(cmd)

    def change(self, column_name):
        cmd = ChangeColumnCommand()
        cmd.column_name = column_name
        self.add_command(cmd)

    def nochange(self, column_name):
        cmd = NochangeColumnCommand()
        cmd.column_name = column_name
        self.add_command(cmd)

    def get_yml(self, verbose=False):
        with closing(StringIO()) as s:
            s.write('%s:\n' % self.action)
            #sorted_tables = sorted(self._tables, key=lambda t: t.lower())
            for col_name in sorted(self.columns.keys(), key=lambda t: t.lower()):
                cmd = self.columns[col_name]
                s.write(indent(cmd.get_yml(verbose) + '\n'))
            return s.getvalue().strip()

    def load_from_dict(self, data):
        for col_name in data:
            value = data[col_name]
            cmd = ColumnCommand()
            cmd.column_name = col_name
            cmd.load_from_string(value)
            self.columns[col_name] = cmd


class ColumnCommand(object):
    action = None

    def __init__(self):
        self.column_name = None

    def get_yml(self, verbose=False):
        return '%s: %s' % (self.column_name, self.action)

    def load_from_string(self, s):
            self.action = s


class NochangeColumnCommand(ColumnCommand):
    action = 'nochange'


class AddColumnCommand(ColumnCommand):
    action = 'add'


class RemoveColumnCommand(ColumnCommand):
    action = 'remove'


class ChangeColumnCommand(ColumnCommand):
    action = 'change'


class RenameColumnCommand(ColumnCommand):
    action = 'renamefrom'

    def __init__(self):
        self.column_name = None
        self.rename_from = None

    def get_yml(self, verbose=False):
        return '%s: %s %s' % (self.column_name, self.action, self.rename_from)

    def load_from_string(self, s):
        m = re.search('(\\w*) (.*)', s)
        self.action = m.group(1)
        self.rename_from = m.group(2)


#ColumnCommand.register(NochangeColumnCommand)
#ColumnCommand.register(AddColumnCommand)
#ColumnCommand.register(RemoveColumnCommand)
#ColumnCommand.register(ChangeColumnCommand)
#ColumnCommand.register(RenameColumnCommand)

TableCommand.register(CreateTableCommand)
TableCommand.register(DropTableCommand)
TableCommand.register(RenameTableCommand)
TableCommand.register(AlterTableCommand)


#=============================================================================
# Migration
#=============================================================================

class Migration(object):
    def __init__(self, previous=None):
        self.previous = previous
        #self.commands = []
        self._tables = {}

    def get_yml(self, verbose=False):
        with closing(StringIO()) as s:
            _write_str(s, "previous: %s\n", self.previous, True)
            if self._tables:
                s.write("tables:\n")
                sorted_tables = sorted(self._tables, key=lambda t: t.lower())
                for table_name in sorted_tables:
                    table_migration = self._tables[table_name]
                    s.write(indent(table_migration.get_yml(verbose) + "\n"))
            else:
                s.write("tables: ~\n")

            return s.getvalue().strip()

    def clear(self):
        self._tables = {}

    def load_from_dict(self, data):
        self.clear()
        self.previous = data["previous"] if "previous" in data else None
        if data["tables"]:
            for table_name in data["tables"]:
                table_migration = TableMigration()
                table_migration.table_name = table_name
                table_migration.load_from_dict(data["tables"][table_name])
                self._tables[table_name] = table_migration

    def load_from_file(self, filename):
        self.clear()
        with file(filename, 'r') as stream:
            string = stream.read()
        self.load_from_str(string)

    def load_from_str(self, string):
        data = yaml.load(string)
        self.load_from_dict(data)

    def save_to_file(self, filename, verbose=False):
        with file(filename, 'w') as stream:
            stream.write(self.get_yml(verbose))

    def add_table_migration(self, table_migration):
        table_name = table_migration.table_name
        self._tables[table_name] = table_migration

    def get_or_create_table_migration(self, table_name):
        if table_name in self._tables:
            table_migration = self._tables[table_name]
        else:
            table_migration = TableMigration()
            table_migration.table_name = table_name
            self._tables[table_name] = table_migration
        return table_migration

    def create_table(self, table_name):
        table_migration = self.get_or_create_table_migration(table_name)
        cmd = CreateTableCommand()
        cmd.table_name = table_name
        table_migration.add_command(cmd)

    def drop_table(self, table_name):
        table_migration = self.get_or_create_table_migration(table_name)
        cmd = DropTableCommand()
        cmd.table_name = table_name
        table_migration.add_command(cmd)

    def rename_table(self, old_name, new_name):
        table_migration = self.get_or_create_table_migration(new_name)
        cmd = RenameTableCommand()
        cmd.table_name = new_name
        cmd.rename_from = old_name
        table_migration.add_command(cmd)

    def alter_table(self, old_table, new_table):
        if new_table.name != old_table.name:
            self.rename_table(old_table.name, new_table.name)
        # Check for renames
        table_migration = self.get_or_create_table_migration(new_table.name)
        cmd = AlterTableCommand()
        cmd.table_name = new_table.name
        renames = {}
        if AlterTableCommand.action in table_migration.commands:
            old_alter = table_migration.commands[AlterTableCommand.action]
            for col_name in old_alter.columns:
                old_action = old_alter.columns[col_name]
                if old_action.action == RenameColumnCommand.action:
                    cmd.columns[col_name] = old_action
                    renames[old_action.rename_from] = old_action
                    renames[col_name] = old_action
        # Add change,nochange,add
        for col in new_table.columns:
            old_col = old_table.get_column(col.name)
            if old_col:
                if col == old_col:
                    cmd.nochange(col.name)
                else:
                    if not col.name in renames:
                        cmd.change(col.name)
                    else:
                        cmd.add(col.name)
            else:
                if not col.name in renames:
                    cmd.add(col.name)
        # Find all the columns that were dropped
        for old_col in old_table.columns:
            if not new_table.get_column(old_col.name):
                if not old_col.name in renames:
                    cmd.remove(old_col.name)
        table_migration.add_command(cmd)

    def get_or_create_table_command(self, table_name, clazz):
        table_migration = self.get_or_create_table_migration(table_name)
        if clazz.action in table_migration.commands:
            cmd = table_migration.commands[clazz.action]
        else:
            cmd = clazz()
            cmd.table_name = table_name
            table_migration.add_command(cmd)
        return cmd

    def rename_column(self, table_name, old_column, new_column):
        cmd = self.get_or_create_table_command(table_name, AlterTableCommand)
        if old_column in cmd.columns:
            if cmd.columns[old_column].action == 'remove':
                del cmd.columns[old_column]
            if cmd.columns[old_column].action == 'change':
                cmd.add(old_column)
        if new_column in cmd.columns:
            if cmd.columns[new_column].action == 'add':
                del cmd.columns[new_column]
            else:
                raise AppError('can not rename %s to %s' % (old_column, new_column))
        cmd.rename(new_column, old_column)

    def add_column(self, table_name, column_name):
        cmd = self.get_or_create_table_command(table_name, AlterTableCommand)
        cmd.add(column_name)

    def change_column(self, table_name, column_name):
        cmd = self.get_or_create_table_command(table_name, AlterTableCommand)
        cmd.change(column_name)

    def remove_column(self, table_name, column_name):
        cmd = self.get_or_create_table_command(table_name, AlterTableCommand)
        cmd.remove(column_name)

    @property
    def tables(self):
        return self._tables

    @tables.setter
    def tables(self):
        raise AttributeError("can't set attribute")


#=============================================================================
# Schema
#=============================================================================

class Schema(object):
    def __init__(self):
        self.version = None
        self._tables = Tables()

    def __repr__(self):
        return "<schema %s>" % repr(self.tables)

    def __eq__(self, other):
        if other is None:
            return False
        else:
            result = self.tables == other.tables
            return result

    @property
    def tables(self):
        return self._tables

    @tables.setter
    def tables(self, tables):
        self._tables = tables

    def get_yml(self, verbose=False):
        with closing(StringIO()) as s:
            s.write("tables:")
            if (self._tables):
                s.write("\n")

                names = sorted(self._tables, key=str.lower)
                for name in names:
                    table = self._tables[name]
                    s.write(indent(table.get_yml(verbose), is_list=True))
                    s.write("\n\n")
            else:
                s.write(" ~\n")
            return s.getvalue().strip()

    def __nonzero__(self):
        if self.tables:
            return len(self.tables)
        else:
            return 0

    def __bool__(self):
        return self.__nonzero__() > 0

    def clear(self):
        self._tables = Tables()

    def load_from_path(self, path, project_root):
        self.clear()
        # Tables
        longpath = os.path.join(path, 'tables/*.yml')
        for filename in glob.glob(longpath):
            t = cache.load(project_root, filename, Table)
            self.add_table(t)

    def load_from_str(self, string):
        data = yaml.load(string)
        self.load_from_dict(data)

    def load_from_dict(self, data):
        if not "tables" in data:
            return
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
        for table_name in self._tables:
            table = self._tables[table_name]
            filename = "%s/tables/%s.yml" % (path, table.name)
            table.save_to_file(filename, verbose)
        # Procedures

    def remove_table(self, name):
        del self._tables[name]

    def add_table(self, table):
        assert table.name
        self._tables[table.name] = table


#=============================================================================
# Release
#=============================================================================

class Release(object):
    def __init__(self):
        self._previous = None
        self._name = None
    pass


#=============================================================================
# Versions
#=============================================================================

class Versions(object):
    def __init__(self, project_root):
        self.project_root = project_root
        self.versions = []
        self._head = None
        self._bootstrap = None

    def append(self, version):
        self.versions.append(version)

    def get_version_by_name(self, name):
        filename = "/versions/%s.yml" % name
        if os.path.exists(self.project_root + filename):
            version = cache.load(self.project_root, filename, Version)
            return version
        else:
            return None

    def get_bootstrap(self):
        if not self._bootstrap:
            self._bootstrap = self.get_version_by_name('bootstrap')
        return self._bootstrap

    def get_head(self):
        if not self._head:
            self._head = self.get_version_by_name('head')
        return self._head

    def get_previous(self, version):
        if version is None:
            return None
        else:
            previous = self.get_version_by_name(version.migration.previous)
            return previous

    def load_from_path(self):
        v = Version()
        v.name = "path"
        v.schema.load_from_path(self.project_root + "/schema", project_root=self.project_root)
#        for filename in glob.glob(self.path + "/schema/tables/*.yml"):
#            print(filename)
#            with file(filename, 'r') as stream:
#                data = yaml.load(stream)
#                v.load_from_dict(data)
        return v


#=============================================================================
# Version
#=============================================================================

class Version(object):
    def __init__(self):
        self.name = None
        self._schema = Schema()
        self.migration = Migration()
        self.filename = None
        self.filehash = None

    def __repr__(self):
        return "<version name='%s' %s>" % (self.name, repr(self._schema.tables))

    def __eq__(self, other):
        return (self.get_yml() == other.get_yml())

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, value):
        self._schema = value

    def get_yml(self, verbose=False):
        with closing(StringIO()) as s:
            _write_str(s, "version: %s\n", self.name, True)
            s.write(self.schema.get_yml(verbose))
            if (self.migration):
                s.write("\nmigration:")
                s.write("\n" + indent(self.migration.get_yml(verbose)))
            else:
                s.write("\nmigration: ~")
            return s.getvalue().rstrip()

    def load_from_str(self, string):
        data = yaml.load(string)
        self.load_from_dict(data)

#    def load_from_file(self, filename=None):
#        if filename:
#            self.filename = filename
#        with file(self.filename, 'r') as stream:
#            string = stream.read()
#        data = yaml.load(string)
#        self.load_from_dict(data)

    def load_from_dict(self, data):
        if "version" in data:
            self.name = data["version"]
        self._schema.load_from_dict(data)
        if "migration" in data:
            self.migration.load_from_dict(data["migration"])

    def save_to_file(self, filename=None, verbose=False):
        if filename is None:
            filename = self.filename
        with file(filename, 'w') as f:
            f.write(self.get_yml(verbose))

    def save_to_path(self, path, verbose=False):
        if not os.path.exists(path):
            os.makedirs(path)
        self.schema.save_to_path(path, verbose)
        self.migration.save_to_file(path + "/migration.yml", verbose)
#
#    def drop_table(self, name):
#        self.schema.remove_table(name)
#        self.migration.add_command(Command(name, 'drop_table'))
#

    def create_table(self, table):
        self.schema.add_table(table)
        self.migration.create_table(table.name)


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
    #print("strings=%s"%strings)
    newlist = [first + strings[0]]
    for i in range(1, len(strings)):
        newlist.append(others + strings[i])

    newstr = "".join(newlist)
    if value[-1] == "\n":
        newstr += "\n"
    return newstr


def output_yaml(value, key_order=None):
    if type(value) is dict:
        if dict:
            with closing(StringIO()) as s:
                if key_order:
                    sorted_keys = key_order
                else:
                    sorted_keys = sorted(value.keys(), key=lambda s: s.lower())
                for key in sorted_keys:
                    if key in value:
                        v = value[key]
                        if type(v) is list or type(v) is dict:
                            if value[key]:
                                yml_output = output_yaml(value[key])
                                s.write('%s:\n' % key)
                                s.write(indent(yml_output + '\n'))
                            else:
                                s.write('%s: ~\n' % key)
                        else:
                            s.write('%s: %s\n' % (key, value[key]))
                r = s.getvalue().strip()
                return r
        else:
            return '~'
    elif type(value) is list:
        if value:
            with closing(StringIO()) as s:
                #s.write('%s:\n' % name)
                for item in value:
                    if type(item) is list:
                        s.write('-\n')
                        s.write(indent(output_yaml(item) + '\n'))
                    elif type(item) is dict:
                        s.write(indent(output_yaml(item) + '\n', indent=0, is_list=True))
                    else:
                        s.write('- %s\n' % item)
                return s.getvalue().strip()
        else:
            return '~'
    else:
        try:
            yml = value.get_yml()
            #print('returning get_yml!!!!')
            return yml
        except:
            #print('returning value!!!!%s' % value)
            return value


#=============================================================================
# main
#=============================================================================

def main():
    pass

if __name__ == '__main__':
    main()
