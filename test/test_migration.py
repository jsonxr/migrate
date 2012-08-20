import unittest
import yaml

import fixtures
import schema


#=============================================================================
# Test Cases
#=============================================================================


COMPLEX = {'table': 'test1',
     'new': 'new_name',
     'list': ['blah',
              {'blah2': ['child1', 'child2']}],
     'params': {
         'one': '1',
         'two': '2',
         'three': {
             'blah': 'blah',
             'blah2': 'blah2'}}}
YML_COMPLEX = '''
list:
    - blah
    - blah2:
          - child1
          - child2
new: new_name
params:
    one: 1
    three:
        blah: blah
        blah2: blah2
    two: 2
table: test1
'''.strip()

DICTIONARY_OF_DICTIONARIES = {
    'one': {
            'a': 'A',
            'b': 'B',
            'c': 'C'
            },
    'two': {
            'A': 'a',
            'B': 'b',
            'C': 'c'
            }
}
YML_DICTIONARY_OF_DICTIONARIES = '''
one:
    a: A
    b: B
    c: C
two:
    A: a
    B: b
    C: c
'''.strip()

LIST_OF_LISTS = [['one', 'two', 'three'], [1, 2, 3]]
YML_LIST_OF_LISTS = '''
-
    - one
    - two
    - three
-
    - 1
    - 2
    - 3
'''.strip()


class TestMigration(unittest.TestCase):

    def test_yaml_output(self):
        value = schema.output_yaml('value')
        assert value == 'value'

        value = schema.output_yaml({'name': 'value'})
        assert value == 'name: value', '\n[%s]' % value

    def test_yaml_dictionary_of_dictionaries(self):
        value = schema.output_yaml(DICTIONARY_OF_DICTIONARIES)
        assert value == YML_DICTIONARY_OF_DICTIONARIES, '\n%s' % value

    def test_yaml_list_of_lists(self):
        value = schema.output_yaml(LIST_OF_LISTS)
        assert value == YML_LIST_OF_LISTS, '\n[%s]' % value

    def test_yaml_complex(self):
        value = schema.output_yaml(COMPLEX)
        assert value == YML_COMPLEX, '\n%s' % value

    @unittest.skip('Skip while we are developing the alter_table command.')
    def test_migration_load_yaml(self):
        with fixtures.TestFixture() as tf:
            expected = tf.get_assert_file("/test_migration/migration_yaml.yml")
            migration = schema.Migration()
            migration.load_from_str(expected)
            yml = migration.get_yml()
            tf.assert_yml_equal_str(yml, expected)

    def test_migration_yaml(self):
        with fixtures.TestFixture() as tf:
            migration = schema.Migration()
            migration.previous = 'bootstrap'
            migration.create_table('changelog')
            migration.rename_table('changelog', 'changelog_old')
            migration.drop_table('old_table')

            old_table = schema.Table()
            old_table.name = 'changelog'
            old_table.columns.add('old_col', 'varchar(2)')
            old_table.columns.add('col2', 'varchar(2)')
            old_table.columns.add('col3', 'varchar(1)')
            old_table.columns.add('col4', 'varchar(255)')

            new_table = schema.Table()
            new_table.name = 'changelog_old'
            new_table.columns.add('old_col', 'varchar1')
            new_table.columns.add('renamed_col', 'varchar(2)')
            new_table.columns.add('col1', 'varchar(1)')
            new_table.columns.add('col4', 'varchar(2)')
            new_table.columns.add('col3', 'varchar(1)')

            migration.alter_table(old_table, new_table)
            migration.rename_column('changelog_old', 'old_col', 'renamed_col')
            migration.alter_table(old_table, new_table)

            # Let's compare!
            yml = migration.get_yml()
            expected = tf.get_assert_file("/test_migration/migration_yaml.yml")
            tf.assert_yml_equal_str(yml, expected)

    @unittest.skip("")
    def test_migration_yaml2(self):
        with fixtures.TestFixture() as tf:
            expected = tf.get_assert_file("/test_migration/migration_yaml.yml")
            data = yaml.load(expected)
            print(data)
            assert False


#=============================================================================
# main
#=============================================================================

def main():
    unittest.main()

if __name__ == '__main__':
    main()
