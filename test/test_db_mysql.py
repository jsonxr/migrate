'''
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
'''
import unittest

import schema
import utils


class TestDbMysql(unittest.TestCase):

    def test_db_empty_schema(self):
        with utils.TestVersion("bootstrap_empty") as tv:
            v = tv.db.get_version()
            assert v.name == "bootstrap"
            #assert v.actual_schema.tables
            assert v.expected_schema is None

    def test_db_version_actual_schema_get_yml(self):
        with utils.TestVersion("datatypes") as tv:
            v = tv.db.get_version()
            assert v.name == "bootstrap"
            assert v.actual_schema is not None
            yml = v.actual_schema.get_yml(verbose=True)
            tv.assert_yml_equal(yml, "/datatypes_schema.yml")
            assert v.expected_schema is None

    def test_db_version_bootstrap_is_syncable(self):
        with utils.TestVersion("bootstrap_empty") as tv:
            v = tv.db.get_version()
            assert v.is_syncable

    def test_db_version_current_is_syncable(self):
        with utils.TestVersion("bootstrap_test1test2") as tv:
            v = tv.db.get_version()
            assert v.is_syncable

    def test_db_converted_schema_to_vendor(self):
        with utils.TestVersion() as tv:
            s = _get_schema_to_convert()
            s = tv.db.convert_schema_to_vendor(s)
            yml = s.get_yml(verbose=True)
            tv.assert_yml_equal(yml, '/converted_schema.yml')


#-----------------------------------------------------------------------------
# Helper functions
#-----------------------------------------------------------------------------

def _get_schema_to_convert():
    s = schema.Schema()
    t = schema.Table("converted")
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

#SQL_DATATYPES = utils.get_resource('/test_db_mysql/datatypes.sql')
#SQL_CURRENT_VERSION = utils.get_resource('/test_db_mysql/current_version.sql')
#YML_DATATYPES_SCHEMA = utils.get_resource('/test_db_mysql/datatypes_schema.yml')
#YML_SCHEMA_CONVERTED = utils.get_resource('/test_db_mysql/schema_converted.yml')
#YML_CURRENT_VERSION = utils.get_resource("/test_db_mysql/current_version.yml")
#YML_BOOTSTRAP_VERSION = utils.get_resource("/test_db_mysql/bootstrap_version.yml")

#-----------------------------------------------------------------------------
# main
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
