'''
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
'''
from _mysql_exceptions import MySQLError
import MySQLdb
import os
import unittest

import db_mysql
import schema

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "j@s0n"

DB_DATABASE_PREFIX = "python_"


class Test(unittest.TestCase):

    def test_db_create_drop(self):
        name = _get_unused_dbname("test_db_create_drop")
        db = _getDatabase(name)
        db.execute_create()
        assert _database_exists(name)
        db.execute_drop()
        assert not _database_exists(name)

    def test_db_empty_schema(self):
        name = _get_unused_dbname("test_db_schema")
        try:
            db = _getDatabase(name)
            db.execute_create()
            v = db.get_version()
            assert v.name == "bootstrap"
            assert v.actual_schema is None
            assert v.expected_schema is None
        finally:
            db.execute_drop()

    def test_db_existing_schema(self):
        """
        Tests all the datatypes
        """
        name = _get_unused_dbname("test_db_existing_schema")
        db = _getDatabase(name)
        try:
            db.execute_create()
            _create_db_schema(name)
            v = db.get_version()
            assert v.name == "bootstrap"
            assert v.actual_schema is not None
            yml = v.actual_schema.get_yml(verbose=True)
            expected = YML_DATATYPES_SCHEMA.strip()
            assert v.expected_schema is None
            assert yml == expected, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)
        finally:
            db.execute_drop()

    def test_db_converted_schema(self):
        """
        Converts int -> int(11)
                 integer -> int(11)
                 etc.
        """
        name = _get_unused_dbname("test_db_converted_schema")
        db = _getDatabase(name)
        expected = YML_SCHEMA_CONVERTED.strip()
        s = _get_schema_to_convert()
        s = db.convert_schema_to_vendor(s)
        yml = s.get_yml(verbose=True)
        assert yml == expected, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)


#-----------------------------------------------------------------------------
# Helper functions
#-----------------------------------------------------------------------------

def _database_exists(name):
    try:
        conn = MySQLdb.connect(host=DB_HOST, user=DB_USER,
                passwd=DB_PASSWORD, db=name)
        conn.close()
        return True
    except MySQLError as e:
        if (e[0] == db_mysql.ER_BAD_DB_ERROR):
            return False
        else:
            raise


def _get_unused_dbname(suffix):
    # We first want to find name that is not already being used
    count = 0
    name = DB_DATABASE_PREFIX + suffix
    while _database_exists(name):
        count += 1
        name = DB_DATABASE_PREFIX + suffix + str(count)
    return name


def _getDatabase(name):
    connection = {"host": DB_HOST, "database": name, "user": DB_USER, "password": DB_PASSWORD}
    db = db_mysql.Database(connection)
    return db


def _create_db_schema(name):
    conn = MySQLdb.connect(host=DB_HOST, user=DB_USER,
            passwd=DB_PASSWORD, db=name)
    filename = os.path.dirname(os.path.realpath(__file__)) + '/resources/mysql_datatypes.sql'
    with file(filename, 'r') as stream:
        sql = stream.read()
    cursor = conn.cursor()
    cursor.execute(sql)

YML_DATATYPES_SCHEMA = """tables:
    - name: datatypes
      columns:
          - { name: "c_bit", type: "bit(1)", key: false, nullable: true, autoincrement: false }
          - { name: "c_bit_64", type: "bit(64)", key: false, nullable: true, autoincrement: false }
          - { name: "c_tinyint", type: "tinyint(4)", key: false, nullable: true, autoincrement: false }
          - { name: "c_tinyint1", type: "tinyint(1)", key: false, nullable: true, autoincrement: false }
          - { name: "c_tinyint4", type: "tinyint(4)", key: false, nullable: true, autoincrement: false }
          - { name: "c_tinyint_u", type: "tinyint(3) unsigned", key: false, nullable: true, autoincrement: false }
          - { name: "c_tinyint_u_z", type: "tinyint(3) unsigned zerofill", key: false, nullable: true, autoincrement: false }
          - { name: "c_bool", type: "tinyint(1)", key: false, nullable: true, autoincrement: false }
          - { name: "c_boolean", type: "tinyint(1)", key: false, nullable: true, autoincrement: false }
          - { name: "c_smallint", type: "smallint(6)", key: false, nullable: true, autoincrement: false }
          - { name: "c_smallint_u", type: "smallint(5) unsigned", key: false, nullable: true, autoincrement: false }
          - { name: "c_smallint_u_z", type: "smallint(5) unsigned zerofill", key: false, nullable: true, autoincrement: false }
          - { name: "c_mediumint", type: "mediumint(9)", key: false, nullable: true, autoincrement: false }
          - { name: "c_mediumint_u", type: "mediumint(8) unsigned", key: false, nullable: true, autoincrement: false }
          - { name: "c_mediumint_u_z", type: "mediumint(8) unsigned zerofill", key: false, nullable: true, autoincrement: false }
          - { name: "c_int", type: "int(11)", key: false, nullable: true, autoincrement: false }
          - { name: "c_integer", type: "int(11)", key: false, nullable: true, autoincrement: false }
          - { name: "c_int_u", type: "int(10) unsigned", key: false, nullable: true, autoincrement: false }
          - { name: "c_int_u_z", type: "int(10) unsigned zerofill", key: false, nullable: true, autoincrement: false }
          - { name: "c_bitint", type: "bigint(20)", key: false, nullable: true, autoincrement: false }
          - { name: "c_bigint_u", type: "bigint(20) unsigned", key: false, nullable: true, autoincrement: false }
          - { name: "c_serial", type: "bigint(20) unsigned", key: true, nullable: false, autoincrement: true }
          - { name: "c_decimal", type: "decimal(10,0)", key: false, nullable: true, autoincrement: false }
          - { name: "c_decimal_money", type: "decimal(65,2)", key: false, nullable: true, autoincrement: false }
          - { name: "c_decimal_u", type: "decimal(10,0) unsigned", key: false, nullable: true, autoincrement: false }
          - { name: "c_decimal_u_z", type: "decimal(10,0) unsigned zerofill", key: false, nullable: true, autoincrement: false }
          - { name: "c_dec", type: "decimal(10,0)", key: false, nullable: true, autoincrement: false }
          - { name: "c_numeric", type: "decimal(10,0)", key: false, nullable: true, autoincrement: false }
          - { name: "c_fixed", type: "decimal(10,0)", key: false, nullable: true, autoincrement: false }
          - { name: "c_float", type: "float", key: false, nullable: true, autoincrement: false }
          - { name: "c_float_u", type: "float unsigned", key: false, nullable: true, autoincrement: false }
          - { name: "c_float_u_z", type: "float unsigned zerofill", key: false, nullable: true, autoincrement: false }
          - { name: "c_double", type: "double", key: false, nullable: true, autoincrement: false }
          - { name: "c_double_u", type: "double unsigned", key: false, nullable: true, autoincrement: false }
          - { name: "c_real", type: "double", key: false, nullable: true, autoincrement: false }
          - { name: "c_date", type: "date", key: false, nullable: true, autoincrement: false }
          - { name: "c_datetime", type: "datetime", key: false, nullable: true, autoincrement: false }
          - { name: "c_timestamp", type: "timestamp", key: false, default: "CURRENT_TIMESTAMP", nullable: false, autoincrement: false }
          - { name: "c_time", type: "time", key: false, nullable: true, autoincrement: false }
          - { name: "c_year", type: "year(4)", key: false, nullable: true, autoincrement: false }
          - { name: "c_year2", type: "year(2)", key: false, nullable: true, autoincrement: false }
          - { name: "c_char", type: "char(1)", key: false, nullable: true, autoincrement: false }
          - { name: "c_char_5", type: "char(5)", key: false, nullable: true, autoincrement: false }
          - { name: "c_varchar_5", type: "varchar(5)", key: false, nullable: true, autoincrement: false }
          - { name: "c_char_binary", type: "char(5)", key: false, nullable: true, autoincrement: false }
          - { name: "c_varchar_binary", type: "varchar(5)", key: false, nullable: true, autoincrement: false }
          - { name: "c_binary", type: "binary(5)", key: false, nullable: true, autoincrement: false }
          - { name: "c_varbinary", type: "varbinary(5)", key: false, nullable: true, autoincrement: false }
          - { name: "c_tinyblob", type: "tinyblob", key: false, nullable: true, autoincrement: false }
          - { name: "c_blob", type: "blob", key: false, nullable: true, autoincrement: false }
          - { name: "c_mediumblob", type: "mediumblob", key: false, nullable: true, autoincrement: false }
          - { name: "c_longblob", type: "longblob", key: false, nullable: true, autoincrement: false }
          - { name: "c_tinytext", type: "tinytext", key: false, nullable: true, autoincrement: false }
          - { name: "c_tinytext_binary", type: "tinytext", key: false, nullable: true, autoincrement: false }
          - { name: "c_text", type: "text", key: false, nullable: true, autoincrement: false }
          - { name: "c_text_binary", type: "text", key: false, nullable: true, autoincrement: false }
          - { name: "c_mediumtext", type: "mediumtext", key: false, nullable: true, autoincrement: false }
          - { name: "c_mediumtext_binary", type: "mediumtext", key: false, nullable: true, autoincrement: false }
          - { name: "c_longtext", type: "longtext", key: false, nullable: true, autoincrement: false }
          - { name: "c_longtext_binary", type: "longtext", key: false, nullable: true, autoincrement: false }
          - { name: "c_enum", type: "enum('x-small','small','medium','large','x-large')", key: false, nullable: true, autoincrement: false }
          - { name: "c_set", type: "set('a','b','c')", key: false, nullable: true, autoincrement: false }
          - { name: "c_set_notnull", type: "set('a','b','c')", key: false, nullable: false, autoincrement: false }"""

YML_SCHEMA_CONVERTED = """tables:
    - name: test
      columns:
          - { name: "integer", type: "int(11)", key: false, nullable: true, autoincrement: false }
          - { name: "int", type: "int(11)", key: false, nullable: true, autoincrement: false }
          - { name: "int unsigned", type: "int(10) unsigned", key: false, nullable: true, autoincrement: false }
          - { name: "smallint", type: "smallint(6)", key: false, nullable: true, autoincrement: false }
          - { name: "smallint unsigned", type: "smallint(5) unsigned", key: false, nullable: true, autoincrement: false }
          - { name: "tinyint", type: "tinyint(4)", key: false, nullable: true, autoincrement: false }
          - { name: "tinyint unsigned", type: "tinyint(10) unsigned", key: false, nullable: true, autoincrement: false }
          - { name: "mediumint", type: "mediumint(9)", key: false, nullable: true, autoincrement: false }
          - { name: "mediumint unsigned", type: "mediumint(10) unsigned", key: false, nullable: true, autoincrement: false }
          - { name: "bigint", type: "bigint(20)", key: false, nullable: true, autoincrement: false }
          - { name: "bigint unsigned", type: "bigint(20) unsigned", key: false, nullable: true, autoincrement: false }
          - { name: "serial", type: "bigint(20) unsigned", key: true, nullable: false, autoincrement: true }
          - { name: "numeric", type: "decimal(10,0)", key: false, nullable: true, autoincrement: false }
          - { name: "fixed", type: "decimal(10,0)", key: false, nullable: true, autoincrement: false }
          - { name: "dec", type: "decimal(10,0)", key: false, nullable: true, autoincrement: false }
          - { name: "dec(1,1)", type: "decimal(1,1)", key: false, nullable: true, autoincrement: false }
          - { name: "decimal", type: "decimal(10,0)", key: false, nullable: true, autoincrement: false }
          - { name: "decimal unsigned", type: "decimal(10,0) unsigned", key: false, nullable: true, autoincrement: false }
          - { name: "real", type: "double", key: false, nullable: true, autoincrement: false }
          - { name: "double precision", type: "double", key: false, nullable: true, autoincrement: false }
          - { name: "bit", type: "bit(1)", key: false, nullable: true, autoincrement: false }
          - { name: "year", type: "year(4)", key: false, nullable: true, autoincrement: false }
          - { name: "timestamp", type: "timestamp", key: false, default: "CURRENT_TIMESTAMP", nullable: false, autoincrement: false }
          - { name: "char", type: "char(1)", key: false, nullable: true, autoincrement: false }
          - { name: "binary", type: "binary(1)", key: false, nullable: true, autoincrement: false }"""


def _get_schema_to_convert():
    s = schema.Schema()
    t = schema.Table("test")
    t.add_column("integer", "integer")
    t.add_column("int", "int")
    t.add_column("int unsigned", "int unsigned")
    t.add_column("smallint", "smallint")
    t.add_column("smallint unsigned", "smallint unsigned")
    t.add_column("tinyint", "tinyint")
    t.add_column("tinyint unsigned", "tinyint unsigned")
    t.add_column("mediumint", "mediumint")
    t.add_column("mediumint unsigned", "mediumint unsigned")
    t.add_column("bigint", "bigint")
    t.add_column("bigint unsigned", "bigint unsigned")
    t.add_column("serial", "serial")
    t.add_column("numeric", "numeric")
    t.add_column("fixed", "fixed")
    t.add_column("dec", "dec")
    t.add_column("dec(1,1)", "dec(1,1)")
    t.add_column("decimal", "decimal")
    t.add_column("decimal unsigned", "decimal unsigned")
    t.add_column("real", "real")
    t.add_column("double precision", "double precision")
    t.add_column("bit", "bit")
    t.add_column("year", "year")
    t.add_column("timestamp", "timestamp")
    t.add_column("char", "char")
    t.add_column("binary", "binary")
    s.add_table(t)
    return s

#-----------------------------------------------------------------------------
# main
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
