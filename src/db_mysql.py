#!/usr/bin/env python
# encoding: utf-8
"""
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
"""

from cStringIO import StringIO
from contextlib import closing
from decorator import decorator
import MySQLdb
import re
import os
import yaml

import config
import database
import dataset
from errors import AppError

import schema
from _mysql_exceptions import MySQLError


##############################################################################
# @connection
# This ensures that the method uses a connection if there isn't one already
# established
##############################################################################

@decorator
def connection(fnc, *args, **kws):
    db = args[0]

    already_connected = db.is_connected()
    if not already_connected:
        db.connect(db.database)

    try:
        result = fnc(*args, **kws)
    finally:
        if not already_connected:
            db.close()

    return result


@decorator
def connectmyql(fnc, *args, **kws):
    db = args[0]

    already_connected = db.is_connected()
    if not already_connected:
        db.connect()

    try:
        result = fnc(*args, **kws)
    finally:
        if not already_connected:
            db.close()

    return result


##############################################################################
# Database
##############################################################################

class Database(database.Database):
    def __init__(self, connection_info):
        self.host = connection_info["host"]
        self.user = connection_info["user"]
        self.password = connection_info["password"]
        self.database = connection_info["database"]
        self.connection = None

    def exists(self):
        connected = False
        try:
            self.connect(self.database)
            self.close()
            connected = True
        except MySQLError as e:
            if e[0] == ER_BAD_DB_ERROR:
                connected = False
            else:
                raise
        return connected

    @connection
    def get_version(self):
        # If the migration_table table does not exist, we return the bootstrap
        # and actual schema
        dbversion = database.DatabaseVersion()
        self._set_actual(dbversion)     # This is the actual
        self._set_expected(dbversion)   # This is the sql_alias converted, verbose
        return dbversion

    def convert_schema_to_vendor(self, s):
        for t in s.tables:
            table = s.tables[t]
            for c in table.columns:
                _convert_column_to_vendor(c)
        return s

    def _set_expected(self, dbversion):
        sql = """select version, yml
            from %s
            order by applied_on_utc desc
            limit 1""" % config.migration_table

        with closing(self.connection.cursor()) as cursor:
            try:
                cursor.execute(sql)
                row = cursor.fetchone()
                dbversion.name = row[0]
                yml = row[1]
                s = schema.Schema()
                s.load_from_str(yml)
                dbversion.expected_schema = s
            except MySQLError as e:
                if e[0] == ER_NO_SUCH_TABLE:
                    dbversion.name = "bootstrap"
                    dbversion.expected_schema = None
                elif e[0] == ER_BAD_FIELD_ERROR:
                    m = "%s is not the expected structure." % config.migration_table
                    raise AppError(m)
                else:
                    raise

    def _set_actual(self, dbversion):
        s = schema.Schema()
        self.__get_tables(s)
        if (s):
            dbversion.actual_schema = s

    def __get_column_headers(self, description):
        headers = dict()
        index = 0
        for colinfo in description:
            headers[colinfo[0]] = index
            index = index + 1
        return headers

    def __get_table_from_row(self, row, column_headers):
            table = schema.Table()
            table.name = row[column_headers['table_name']]
            return table

    def __get_column_from_row(self, row, column_headers):
        column = schema.Column()
        column.name = row[1]
        column.position = row[2]
        column.type = row[4].lower()
        if (not row[3] is None):
            column.default = str(row[3])
        if row[5] == "YES":
            column.nullable = True
        else:
            column.nullable = False
        column.precision = row[7]
        column.scale = row[8]
        if row[9] == "PRI":
            column.key = True
        if row[10] == "auto_increment":
            column.autoincrement = True

        return column

    @connection
    def __get_tables(self, myschema):
        # Tables
        sql = """
        select table_name, engine, table_rows, auto_increment
        from information_schema.tables
        where table_schema = '""" + self.database + """'
        order by table_schema, table_name
        """
        cursor = self.connection.cursor()
        cursor.execute(sql)
        column_headers = self.__get_column_headers(cursor.description)

        rows = cursor.fetchall()
        cursor.close()
        for row in rows:
            table = self.__get_table_from_row(row, column_headers)
            myschema.tables[table.name] = table

        # Columns
        sql = """
        select table_name, column_name, ordinal_position, column_default,
            column_type, is_nullable, character_maximum_length,
            numeric_precision, numeric_scale, column_key, extra
        from information_schema.columns
        where table_schema = '""" + self.database + """'
        order by table_schema, table_name, ordinal_position
        """
        cursor = self.connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        column_headers = self.__get_column_headers(cursor.description)

        cursor.close()
        for row in rows:
            table_name = row[0]
            table = myschema.tables[table_name]

            column = self.__get_column_from_row(row, column_headers)
            table.columns.append(column)

        # Foreign Keys
        sql = """
        select table_name, constraint_name, column_name, ordinal_position,
            position_in_unique_constraint, referenced_table_name,
            referenced_column_name
        from  information_schema.key_column_usage
        where table_schema = '""" + self.database + """'
        order by table_name, constraint_name
        """
        cursor = self.connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        #print rows

    def is_connected(self):
        return not (self.connection is None)

    def connect(self, database_name=None):
        if (database_name):
            self.connection = MySQLdb.connect(host=self.host, user=self.user,
                    passwd=self.password, db=database_name)
        else:
            self.connection = MySQLdb.connect(host=self.host, user=self.user,
                    passwd=self.password)
        return self.connection

    def close(self):
        self.connection.close()
        self.connection = None

    @connectmyql
    def execute_create(self):
        try:
            sql = "CREATE DATABASE " + self.database
            cursor = self.connection.cursor()
            cursor.execute(sql)
            cursor.close()
        except MySQLError as e:
            if e[0] == ER_DB_CREATE_EXISTS:
                raise AppError("%s already exists." % self.database)
            else:
                raise

    @connectmyql
    def execute_drop(self):
        try:
            sql = "DROP DATABASE " + self.database
            cursor = self.connection.cursor()
            cursor.execute(sql)
            cursor.close()
        except MySQLError as e:
            if e[0] == ER_DB_DROP_EXISTS:
                raise AppError("%s does not exist." % self.database)
            else:
                raise

##############################################################################
# Please review the below
##############################################################################

    @property
    def schema(self):
        myschema = None
        self.connect(self.database)
        try:
            myschema = self.__get_schema()
        finally:
            self.close()
        return myschema

    @property
    def is_expected(self):
        self.connect(self.database)
        myschema = schema.Schema()

        try:
            sql = "select * from {s}" % config.migration_table
            cursor = self.connection.cursor()
            cursor.execute(sql)
        except MySQLError as e:
            if e[0] == ER_NO_SUCH_TABLE:
                myschema.version = None
            else:
                raise

        return True

    def __get_schema(self):
        # Validate mysql version
        # TODO: show variables like "version";
        myschema = schema.Schema()
        self.__get_version(myschema)
        self.__get_tables(myschema)
        #self.__get_procedures(myschema)
        return myschema

    def sync(self, change_set, yml_schema):
        self.connect(self.database)
#        try:
#            if change_set.create_tables:
#                for table_name in schema.caseinsensitive_sort(change_set.create_tables):
#                    table = change_set.left_schema.tables[table_name]
#                    sql = self.__get_create_sql_for_table(table)
#                    print sql
                    #self.__execute(sql)

#            if change_set.alter_tables:
#                for table_name in schema.caseinsensitive_sort(change_set.alter_tables):
#                    old = change_set.alter_tables[table_name].right
#                    table = change_set.left_schema.tables[table_name]
#
#                    for column in table.columns:
#                        print "---------"
#                        print column.get_yaml()
#                        oc = old.get_column_by_name(column.name)
#                        print oc.get_yaml()
#
#                    sql = self.__get_alter_sql_for_table(table, old)
#                    print sql
                    #self.__execute(sql)

#            if change_set.drop_tables:
#                for table_name in schema.caseinsensitive_sort(change_set.drop_tables):
#                    sql = self.__get_drop_sql_for_table(table_name)
#                    print sql
                    #self.__execute(sql)
#        finally:
#            self.close()

    def get_dataset(self):
        self.connect(self.database)
        try:
            data = dataset.Dataset()
            data.schema = self.__get_schema()
            for table_name in data.schema.tables:
                results = self.__select("select * from %s" % table_name)
                t = dataset.Table()
                t.table = data.schema.tables[table_name]

                # headers = sorted(results["headers"].iteritems(),
                #                  key=operator.itemgetter(1)) # sort by key
                # header_row = [header[0] for header in headers]
                # t.headers = header_row
                t.columns = results["columns"]
                t.rows = results["rows"]
                yml = t.get_yaml()
                if yml:
                    print t.get_yaml()
        finally:
            self.close()

    def __get_drop_sql_for_table(self, table_name):
        return "DROP TABLE `%s`;" % table_name

    def __get_create_sql_for_table(self, table):
        s = StringIO()

        s.write("CREATE TABLE `%s` (\n" % table.name)
        primary_keys = list()
        index = 0
        for column in table.columns:
            if (column.key):
                primary_keys.append('`' + column.name + '`')

            s.write("  `%s` %s" % (column.name, column.type))
            if (not column.nullable):
                s.write(" NOT NULL")
            if (index + 1 < len(table.columns) or primary_keys):
                s.write(",")
            s.write("\n")
            index = index + 1
        if primary_keys:
            s.write("  PRIMARY KEY (%s)\n" % ",".join(primary_keys))
        s.write(") ENGINE=InnoDB")

        return_str = s.getvalue()
        s.close()
        return return_str

    def __get_alter_sql_for_table(self, table, old):
        s = StringIO()

        s.write("ALTER TABLE `%s`\n" % table.name)
        for index in range(len(table.columns)):
            column = table.columns[index]
            if index == 0:
                after = "FIRST"
            else:
                after = "AFTER `%s`" % (table.columns[index - 1].name)
            if old.get_column_by_name(column.name):
                s.write("  CHANGE COLUMN `%s` `%s` %s %s" % (column.name,
                                                             column.name,
                                                             column.type,
                                                             after))
            else:
                s.write("  ADD COLUMN `%s` %s %s" % (column.name, column.name,
                                                     column.type, after))
            if (index + 1) < len(table.columns):
                s.write(",\n")
            else:
                s.write(";\n")

        return_str = s.getvalue()
        s.close()
        return return_str

    def __execute(self, sql):
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()
        cursor.close()

    def __select(self, sql):
        cursor = self.connection.cursor()
        cursor.execute(sql)
        column_headers = cursor.description

        rows = cursor.fetchall()
        cursor.close()
        return {"columns": column_headers, "rows": rows}

    def __get_version(self, myschema):
        if (self.connection is None):
            raise AppError("Connection not established.")
        sql = "select version from " + config.migration_table
        sql += " order by applied_at desc limit 1"

        cursor = self.connection.cursor()
        try:
            cursor.execute(sql)
            #column_headers = self.__get_column_headers(cursor.description)
            row = cursor.fetchone()
            print row
            myschema.version = row[0]
        except MySQLError as e:
            if e[0] == ER_NO_SUCH_TABLE:
                myschema.version = None
            elif e[0] == ER_BAD_FIELD_ERROR:
                m = "%s is not the expected structure." % config.migration_table
                raise AppError(m)
            else:
                raise
        finally:
            cursor.close()

    def __get_procedures(self, myschema):
        sql = """
        select name, body_utf8, comment, param_list, returns
        from mysql.proc
        where db = '""" + self.database + """'
        and type='PROCEDURE' and language='SQL'
        """
        cursor = self.connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        for row in rows:
            procedure = schema.Procedure()
            procedure.name = row[0]
            procedure.body = row[1]
            procedure.comment = row[2]

            if (row[3]):
                parameters = [x.strip() for x in row[3].split(',')]

                for param in parameters:
                    m = re.search('(.*) (.*) (.*)', 'in test varchar(255)')
                    param = schema.Parameter()
                    param.mode = m.group(1)
                    param.name = m.group(2)
                    #param_type = m.group(3)
                    procedure.parameters.append(param)

            myschema.procedures[procedure.name] = procedure

#-----------------------------------------------------------------------------
# Load Type mappings
#-----------------------------------------------------------------------------

filename = os.path.dirname(os.path.realpath(__file__)) + '/resources/mysql.yml'
with file(filename, 'r') as stream:
    data = yaml.load(stream)
    sql_aliases = []
    for sr in data["sql_aliases"]:
        alias = {"search": re.compile(sr["search"]), "replace": sr["replace"]}
        if "attributes" in sr:
            alias["attributes"] = sr["attributes"]
        sql_aliases.append(alias)

    sql_to_type = []
    for sr in data["sql_to_yml"]:
        sql_to_type.append({"search": re.compile(sr["search"]), "replace": sr["replace"]})


def _convert_column_to_vendor(column):
    new_type = column.type
    for sr in sql_aliases:
        search = sr["search"]
        replace = sr["replace"]
        result = search.subn(replace, new_type)
        if result[1] >= 1:
            new_type = result[0]
            if "attributes" in sr:
                for attr in sr["attributes"]:
                    column.__dict__[attr] = sr["attributes"][attr]
    column.type = new_type


#def _sql_to_type(sql_type):
#    new_type = sql_type
#    for sr in sql_to_type:
#        search = sr["search"]
#        replace = sr["replace"]
#        result = search.subn(replace, new_type)
#        if result[1] >= 1:
#            new_type = result[0]
#    return new_type

#-----------------------------------------------------------------------------
# MySQL constants
#
# from http://dev.mysql.com/doc/refman//5.5/en/error-messages-server.html
#-----------------------------------------------------------------------------

ER_DB_CREATE_EXISTS = 1007
ER_DB_DROP_EXISTS = 1008
ER_BAD_DB_ERROR = 1049
ER_BAD_FIELD_ERROR = 1054
ER_NO_SUCH_TABLE = 1146


def main():
    pass

if __name__ == '__main__':
    main()
