'''
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
'''
import unittest

import schema
import fixtures


class TestDbMysql(unittest.TestCase):

    def test_get_actual_schema_empty(self):
        with fixtures.TestFixture("bootstrap_empty") as tf:
            s = tf.db.get_actual_schema()
            assert not s, "Schema should be empty"

    def test_get_actual_schema(self):
        with fixtures.TestFixture("bootstrap_test1test2") as tf:
            s = tf.db.get_actual_schema()
            assert s, "Schema is empty"
            assert len(s.tables) == 2
            assert "test1" in s.tables
            assert "test2" in s.tables
            yml = s.get_yml()
            tf.assert_yml_equal_file(yml, "/test_db_mysql/test1test2_schema.yml")

    def test_get_expected_version_empty(self):
        with fixtures.TestFixture("bootstrap_test1test2") as tf:
            v = tf.db.get_expected_version()
            assert not v, "Version should be empty"

    def test_get_expected_version(self):
        with fixtures.TestFixture("head_test1test2") as tf:
            v = tf.db.get_expected_version()
            assert v, "Version should not be empty"
            assert v.name == 'head', "Version name should be head"
            yml = v.get_yml()
            tf.assert_yml_equal_file(yml, '/test_db_mysql/test1test2_version.yml')

    def test_get_version_by_name(self):
        with fixtures.TestFixture("head_test1test2") as tf:
            v = tf.db.get_version('bootstrap')
            assert v, "Version should not be empty"
            assert v.name == 'bootstrap', "Version name should be head"
            yml = v.get_yml()
            bootstrap_yml = tf.get_resource('/project/versions/bootstrap.yml')
            tf.assert_yml_equal_str(yml, bootstrap_yml)

    @unittest.skip('')
    def test_db_version_actual_schema_get_yml(self):
        with fixtures.TestFixture("datatypes") as tf:
            v = tf.db.get_version()
            assert v.name == "bootstrap"
            assert v.actual_schema is not None
            yml = v.actual_schema.get_yml()
            tf.assert_yml_equal_file(yml, "/datatypes_schema.yml")
            assert v.expected_schema is None

    @unittest.skip("is_syncable should move to project...")
    def test_db_bootstrap_empty_is_syncable(self):
        with fixtures.TestFixture("bootstrap_empty") as tf:
            #assert tf.project.is_syncable
            versions = schema.Versions(tf.temp_path)
            bootstrap = versions.get_bootstrap()
            v = tf.db.get_version(bootstrap)
            assert v.is_syncable

    @unittest.skip("is_syncable should move to project...")
    def test_db_bootstrap_test1test2_is_syncable(self):
        with fixtures.TestFixture("bootstrap_test1test2") as tf:
            versions = schema.Versions(tf.temp_path)
            bootstrap = versions.get_bootstrap()
            v = tf.db.get_version(bootstrap)
            assert v.is_syncable

    @unittest.skip("is_syncable should move to project...")
    def test_db_version_head_is_syncable(self):
        with fixtures.TestFixture("head_test1test2", clean=True) as tf:
            versions = schema.Versions(tf.temp_path)
            bootstrap = versions.get_bootstrap()
            v = tf.db.get_version(bootstrap)
            assert v.is_syncable

    def test_db_converted_schema_to_vendor(self):
        with fixtures.TestFixture() as tf:
            s = _get_schema_to_convert()
            s = tf.db.convert_schema_to_vendor(s)
            yml = s.get_yml()
            tf.assert_yml_equal_file(yml, '/converted_schema.yml')


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
# main
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
