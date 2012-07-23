import unittest

import schema


#=============================================================================
# Schema Yml Tests
#=============================================================================
class TestColumns(unittest.TestCase):
    @unittest.skip("Not supporting the getattr/setattr until can figure out pickle problem")
    def test_columns_getattr_setattr(self):
        columns = schema.Columns()
        c = schema.Column("col1", "string")
        columns.append(c)
        c = columns.col1
        assert c

    @unittest.skip("Not supporting the getattr/setattr until can figure out pickle problem")
    def test_columns_getattr_setattr_keyerror(self):
        columns = schema.Columns()
        c = schema.Column("col1", "string")
        columns.append(c)
        try:
            c = columns.col2
        except KeyError as e:
            assert e[0] == 'col2'
        else:
            assert False

    def test_columns_eq(self):
        c1 = schema.Columns()
        c1.append(schema.Column("one", "string"))
        c1.append(schema.Column("two", "string", key=True))
        c2 = schema.Columns()
        c2.append(schema.Column("one", "string"))
        c2.append(schema.Column("two", "string", key=True))
        assert c1 == c2

    def test_columns_not_eq(self):
        c1 = schema.Columns()
        c1.append(schema.Column("one", "string"))
        c1.append(schema.Column("two", "string", key=False))
        c2 = schema.Columns()
        c2.append(schema.Column("one", "string"))
        c2.append(schema.Column("two", "string", key=True))
        assert c1 != c2


#=============================================================================
# main
#=============================================================================

def main():
    unittest.main()

if __name__ == '__main__':
    main()
