import unittest

import os
import shutil
import tempfile
import yaml

import schema


#=============================================================================
# Schema Yml Tests
#=============================================================================

class SchemaYmlTests(unittest.TestCase):

    def testYamlToMigration(self):
        expected = YML_MIGRATION.strip()
        data = yaml.load(expected)
        m = schema.Migration()
        m.load_from_dict(data)
        yml = m.get_yml()
        assert yml == expected, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)

    def testMigrationToYaml(self):
        m = _create_yml_migration()
        yml = m.get_yml()
        expected = YML_MIGRATION.strip()
        assert yml == expected, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)

    def testYamlToVersion(self):
        expected = YML_VERSION.strip()
        data = yaml.load(expected)
        v = schema.Version()
        v.load_from_dict(data)
        yml = v.get_yml(verbose=True)
        assert yml == expected, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)

    def testVersionToYaml(self):
        expected = YML_VERSION.strip()
        v = _create_yml_version()
        yml = v.get_yml(True)
        assert yml == expected, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)

    def testPathToSchema(self):
        expected = YML_TABLE_VERBOSE.strip()
        path = tempfile.mkdtemp()
        try:
            os.mkdir(path + '/tables')
            with file(path + '/tables/test1.yml', 'w') as stream:
                stream.write(YML_TABLE)
            t = _create_yml_table()
            yml = t.get_yml(verbose=True)
            assert yml == expected, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)
        finally:
            shutil.rmtree(path)  # Make sure we clean up after ourselves

    def testSchemaToPath(self):
        expected = YML_TABLE.strip()
        s = _create_yml_schema()
        path = tempfile.mkdtemp()
        try:
            s.save_to_path(path)
            assert os.path.exists(path + "/tables")
            assert os.path.exists(path + "/tables/test1.yml")
            with file(path + "/tables/test1.yml") as stream:
                yml = stream.read()
            assert yml == expected, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)
        finally:
            shutil.rmtree(path)  # Make sure we clean up after ourselves

    def testYamlToSchema(self):
        expected = YML_SCHEMA.strip()
        data = yaml.load(expected)
        s = schema.Schema()
        s.load_from_dict(data)
        yml = s.get_yml(verbose=True)
        assert yml == expected, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)

    def testSchemaToYaml(self):
        expected = YML_SCHEMA.strip()
        s = _create_yml_schema()
        yml = s.get_yml(verbose=True)
        assert yml == expected, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)

    def testTableToFilename(self):
        expected = YML_TABLE.strip()
        filename = tempfile.mktemp(suffix=".yml")
        try:
            t = _create_yml_table()
            t.save_to_file(filename)
            with file(filename, 'r') as stream:
                yml = stream.read()
            assert yml == expected, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)
        finally:
            os.remove(filename)  # Make sure we clean up after ourselves

    def testYamlToTable(self):
        expected = YML_TABLE.strip()
        data = yaml.load(expected)
        t = schema.Table()
        t.load_from_dict(data)
        yml = t.get_yml()
        assert yml == expected, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)

    def testTableToYaml(self):
        expected = YML_TABLE.strip()
        t = _create_yml_table()
        yml = t.get_yml()
        assert yml == expected, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)

    def testIndent(self):
        original = """name"""
        result = schema.indent(original)
        expected = """    name"""
        assert expected == result


#=============================================================================
# Table YML
#=============================================================================

YML_TABLE = """name: test1
columns:
    - { name: "col1", type: "string" }
    - { name: "col2", type: "string", key: true, nullable: false }"""

YML_TABLE_VERBOSE = """name: test1
columns:
    - { name: "col1", type: "string", key: false, nullable: true, autoincrement: false }
    - { name: "col2", type: "string", key: true, nullable: false, autoincrement: false }"""


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

YML_SCHEMA = """tables:
    - name: test1
      columns:
          - { name: "col1", type: "string", key: false, nullable: true, autoincrement: false }
          - { name: "col2", type: "string", key: true, nullable: false, autoincrement: false }
    - name: test2
      columns:
          - { name: "col1", type: "string", key: false, nullable: true, autoincrement: false }
          - { name: "col2", type: "string", key: true, nullable: false, autoincrement: false }
    - name: test3
      columns:
          - { name: "col1", type: "string", key: false, nullable: true, autoincrement: false }
          - { name: "col2", type: "string", key: true, nullable: false, autoincrement: false }"""


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

YML_MIGRATION = """previous: ~
commands:
    - { table: altered_table, name: add_column, column: added_column }
    - { table: altered_table, name: change_column, column: changed_column }
    - { table: altered_table, name: remove_column, column: dropped_column }
    - { table: altered_table, name: rename_column, column: renamed_column, old: old_column }
    - { table: migration, name: create_table }
    - { table: migration_bak, name: rename_table, old: migration }
    - { table: migration_old, name: drop_table }"""


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

YML_VERSION = """version: current
hash: 7b1702d8ee0b77cad4674f5998f2f0dc0246d68e
tables:
    - name: test1
      columns:
          - { name: "col1", type: "string", key: false, nullable: true, autoincrement: false }
          - { name: "col2", type: "string", key: true, nullable: false, autoincrement: false }
migration:
    previous: bootstrap
    commands:
        - { table: test1, name: create_table }"""


def _create_yml_version():
    v = schema.Version()
    v.migration.previous = "bootstrap"
    v.name = "current"
    t = _create_yml_table()
    v.create_table(t)
    return v


#=============================================================================
# main
#=============================================================================

def main():
    unittest.main()

if __name__ == '__main__':
    main()
