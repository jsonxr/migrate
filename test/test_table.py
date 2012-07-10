import unittest

import schema


#=============================================================================
# Table
#=============================================================================
class TestTable(unittest.TestCase):
    def test_tables_getattr_setattr(self):
        tables = schema.Tables()
        tables.bob = schema.Table("bob")
        t = tables.bob
        assert t

    def test_tables_getattr_setattr_keyerror(self):
        tables = schema.Tables()
        t = tables.frank
        assert t is None  # Just here to prevent a warning

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
