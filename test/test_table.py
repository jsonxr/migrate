import unittest

import schema
import fixtures


#=============================================================================
# Table
#=============================================================================
class TestTable(unittest.TestCase):

    def test_tables_create(self):
        with fixtures.TestFixture() as tf:
            table = schema.Table()
            table.name = 'changelog'
            table.columns.add('old_col', 'varchar(1)')
            table.columns.add('col2', 'varchar(1)')
            table.columns.add('col3', 'varchar(1)')
            # Let's compare!
            yml = table.get_yml()
            expected = tf.get_assert_file("/test_table/changelog.yml")
            tf.assert_yml_equal_str(yml, expected)

    @unittest.skip("Not supporting the getattr/setattr until can figure out pickle problem")
    def test_tables_getattr_setattr(self):
        tables = schema.Tables()
        tables.bob = schema.Table("bob")
        t = tables.bob
        assert t

    @unittest.skip("Not supporting the getattr/setattr until can figure out pickle problem")
    def test_tables_getattr_setattr_keyerror(self):
        tables = schema.Tables()
        t = tables.frank
        assert t is None  # Just here to prevent a warning

    @unittest.skip("Not supporting the getattr/setattr until can figure out pickle problem")
    def test_tables_getattr_setattr_mismatch_tablename(self):
        tables = schema.Tables()
        try:
            tables.bob = schema.Table("frank")
        except KeyError as e:
            assert e[0] == "bob"  # Should throw an error
        else:
            assert False, "tables.bob should throw a KeyError"


#=============================================================================
# main
#=============================================================================

def main():
    unittest.main()

if __name__ == '__main__':
    main()
