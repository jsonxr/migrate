'''
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
'''
import datetime
import getpass
import MySQLdb
import socket
import unittest

import schema
import utils


class TestDbMysql(unittest.TestCase):
    def test_db_create_drop(self):
        db = utils.get_database()
        db.execute_create()
        assert utils.database_exists()
        db.execute_drop()
        assert not utils.database_exists()

    def test_db_empty_schema(self):
        try:
            db = utils.get_database()
            db.execute_create()
            v = db.get_version()
            assert v.name == "bootstrap"
            #assert v.actual_schema.tables
            assert v.expected_schema is None
        finally:
            db.execute_drop()

    def test_db_version_actual_schema_get_yml(self):
        db = utils.get_database()
        try:
            db.execute_create()
            _create_db_schema()
            v = db.get_version()
            assert v.name == "bootstrap"
            assert v.actual_schema is not None
            yml = v.actual_schema.get_yml(verbose=True)
            expected = YML_DATATYPES_SCHEMA.strip()
            assert v.expected_schema is None
            assert yml == expected, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)
        finally:
            db.execute_drop()

    def test_db_version_bootstrap_is_syncable(self):
        db = utils.get_database()
        try:
            db.execute_create()
            _create_db_schema()
            v = db.get_version()
            assert v.is_syncable
        finally:
            db.execute_drop()

    def test_db_version_current_is_syncable(self):
        db = utils.get_database()
        try:
            db.execute_create()
            _create_db_schema_current_version()
            v = db.get_version()
            assert v.is_syncable
        finally:
            db.execute_drop()

    def test_db_converted_schema_to_vendor(self):
        db = utils.get_database()
        expected = YML_SCHEMA_CONVERTED.strip()
        s = _get_schema_to_convert()
        s = db.convert_schema_to_vendor(s)
        yml = s.get_yml(verbose=True)
        assert yml == expected, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)


#-----------------------------------------------------------------------------
# Helper functions
#-----------------------------------------------------------------------------


def _create_db_schema():
    conn = MySQLdb.connect(host=utils.DB_HOST, user=utils.DB_USER,
            passwd=utils.DB_PASSWORD, db=utils.DB_DATABASE)
    sql = SQL_DATATYPES
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    conn.commit()
    conn.close()


def _create_db_schema_current_version():
    conn = MySQLdb.connect(host=utils.DB_HOST, user=utils.DB_USER,
            passwd=utils.DB_PASSWORD, db=utils.DB_DATABASE)
    sql = SQL_CURRENT_VERSION
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    conn.commit()

    sql = "INSERT INTO migrations (version, yml, applied_by, applied_on) values (%s,%s,%s,%s)"
    username = socket.gethostname() + "/" + getpass.getuser()
    values = [
              ('bootstrap', YML_BOOTSTRAP_VERSION, username, datetime.datetime.now()),
              ('current', YML_CURRENT_VERSION, username, datetime.datetime.now()),
              ]
    cursor = conn.cursor()
    cursor.executemany(sql, values)
    cursor.close()
    conn.commit()

    #cursor.close()
    conn.close()


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
# Resources
#-----------------------------------------------------------------------------

SQL_DATATYPES = utils.get_resource('/test_db_mysql/datatypes.sql')
SQL_CURRENT_VERSION = utils.get_resource('/test_db_mysql/current_version.sql')
YML_DATATYPES_SCHEMA = utils.get_resource('/test_db_mysql/datatypes_schema.yml')
YML_SCHEMA_CONVERTED = utils.get_resource('/test_db_mysql/schema_converted.yml')
YML_CURRENT_VERSION = utils.get_resource("/test_db_mysql/current_version.yml")
YML_BOOTSTRAP_VERSION = utils.get_resource("/test_db_mysql/bootstrap_version.yml")

#-----------------------------------------------------------------------------
# main
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
