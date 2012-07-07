import unittest

import os
import shutil
import tempfile
import yaml

import schema
import utils


#=============================================================================
# Schema Yml Tests
#=============================================================================

class TestYml(unittest.TestCase):
    def test_migration_load_from_dict(self):
        expected = YML_MIGRATION.strip()
        data = yaml.load(expected)
        m = schema.Migration()
        m.load_from_dict(data)
        yml = m.get_yml()
        utils.assert_yml_equal(yml, expected)

    def test_migration_get_yml(self):
        m = _create_yml_migration()
        yml = m.get_yml()
        expected = YML_MIGRATION.strip()
        utils.assert_yml_equal(yml, expected)

    def test_version_load_from_dict(self):
        expected = YML_VERSION_VERBOSE.strip()
        data = yaml.load(expected)
        v = schema.Version()
        v.load_from_dict(data)
        yml = v.get_yml(verbose=True)
        utils.assert_yml_equal(yml, expected)

    def test_version_get_yml(self):
        expected = YML_VERSION_VERBOSE.strip()
        v = _create_yml_version()
        yml = v.get_yml(True)
        utils.assert_yml_equal(yml, expected)

    def test_table_load_from_file(self):
        expected = YML_TABLE_VERBOSE.strip()
        path = tempfile.mkdtemp()
        try:
            filename = path + '/tables/test1.yml'
            os.mkdir(path + '/tables')
            with file(filename, 'w') as stream:
                stream.write(YML_TABLE)
            t = schema.Table()
            t.load_from_file(filename)
            yml = t.get_yml(verbose=True)
            utils.assert_yml_equal(yml, expected)
        finally:
            shutil.rmtree(path)  # Make sure we clean up after ourselves

    def test_schema_save_to_path(self):
        expected = YML_TABLE.strip()
        s = _create_yml_schema()
        path = tempfile.mkdtemp()
        try:
            s.save_to_path(path)
            assert os.path.exists(path + "/tables")
            assert os.path.exists(path + "/tables/test1.yml")
            with file(path + "/tables/test1.yml") as stream:
                yml = stream.read()
            utils.assert_yml_equal(yml, expected)
        finally:
            shutil.rmtree(path)  # Make sure we clean up after ourselves

    def test_schema_load_from_dict(self):
        expected = YML_SCHEMA_VERBOSE.strip()
        data = yaml.load(expected)
        s = schema.Schema()
        s.load_from_dict(data)
        yml = s.get_yml(verbose=True)
        utils.assert_yml_equal(yml, expected)

    def test_schema_get_yml(self):
        expected = YML_SCHEMA_VERBOSE.strip()
        s = _create_yml_schema()
        yml = s.get_yml(verbose=True)
        utils.assert_yml_equal(yml, expected)

    def test_table_save_to_file(self):
        expected = YML_TABLE.strip()
        filename = tempfile.mktemp(suffix=".yml")
        try:
            t = _create_yml_table()
            t.save_to_file(filename)
            with file(filename, 'r') as stream:
                yml = stream.read()
            utils.assert_yml_equal(yml, expected)
        finally:
            os.remove(filename)  # Make sure we clean up after ourselves

    def test_table_load_from_dict(self):
        expected = YML_TABLE.strip()
        data = yaml.load(expected)
        t = schema.Table()
        t.load_from_dict(data)
        yml = t.get_yml()
        utils.assert_yml_equal(yml, expected)

    def test_table_get_yml(self):
        expected = YML_TABLE.strip()
        t = _create_yml_table()
        yml = t.get_yml()
        utils.assert_yml_equal(yml, expected)

    def test_indent(self):
        original = """name"""
        result = schema.indent(original)
        expected = """    name"""
        assert expected == result


#=============================================================================
# Table YML
#=============================================================================


def _create_yml_table():
    t = schema.Table()
    t.name = "test1"
    t.add_column("col1", "string")
    c = t.add_column("col2", "string")
    c.nullable = False
    c.key = True
    return t


#=============================================================================
# Schema YML
#=============================================================================


def _create_yml_schema():
    s = schema.Schema()
    t = _create_yml_table()
    t.name = "test2"
    s.add_table(t)

    t = _create_yml_table()
    t.name = "test3"
    s.add_table(t)

    t = _create_yml_table()
    s.add_table(t)
    return s


#=============================================================================
# Migration YML
#=============================================================================

def _create_yml_migration():
    m = schema.Migration()
    m.add_command(schema.Command("migration", "create_table"))
    m.add_command(schema.Command("migration_bak", "rename_table", old="migration"))
    m.add_command(schema.Command("migration_old", "drop_table"))
    m.add_command(schema.Command("altered_table", "rename_column", column="renamed_column", old="old_column"))
    m.add_command(schema.Command("altered_table", "add_column", column="added_column"))
    m.add_command(schema.Command("altered_table", "remove_column", column="dropped_column"))
    m.add_command(schema.Command("altered_table", "change_column", column="changed_column"))

    return m


#=============================================================================
# Version YML
#=============================================================================

def _create_yml_version():
    v = schema.Version()
    v.migration.previous = "bootstrap"
    v.name = "current"
    t = _create_yml_table()
    v.create_table(t)
    return v


#=============================================================================
# YML comparison files
#=============================================================================

YML_TABLE = utils.get_resource('/test_yaml/table.yml')
YML_TABLE_VERBOSE = utils.get_resource('/test_yaml/table_verbose.yml')
YML_SCHEMA_VERBOSE = utils.get_resource('/test_yaml/schema_verbose.yml')
YML_MIGRATION = utils.get_resource('/test_yaml/migration.yml')
YML_VERSION_VERBOSE = utils.get_resource('/test_yaml/version_verbose.yml')


#=============================================================================
# main
#=============================================================================

def main():
    unittest.main()

if __name__ == '__main__':
    main()
