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
        try:
            t = tables.frank
            assert t  # Just here to prevent a warning
        except KeyError as e:
            assert e[0] == "frank"
        else:
            assert False, "table 'frank' should not exist"

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
