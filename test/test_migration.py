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

    def test_migration_yaml(self):
        with fixtures.TestFixture() as tf:
            migration = schema.Migration()
            migration.previous = 'bootstrap'
            # create
            m = schema.TableMigration()
            m.table_name = 'changelog'
            m.create()
            migration.add_table_migration(m)

            # rename
            m = schema.TableMigration()
            m.table_name = 'changelog_old'
            m.rename('changelog')
            # alter
            c = schema.AlterTableCommand()
#            old_col: add_column
#            renamed_col: { renamefrom: old_col }
#            col1: add_column
#            col3: ~
#            col4: change_column
#            col2: remove_column
            c.add('old_col')
            c.rename('renamed_col', 'old_col')
            c.add('col1')
            c.change('col3')
            c.nochange('col4')
            c.remove('col2')
            m.add_command(c)
            #m.add_command(c)
            migration.add_table_migration(m)

            # drop
            m = schema.TableMigration()
            m.table_name = 'old_table'
            m.drop()
            migration.add_table_migration(m)

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
