import unittest

import schema


#=============================================================================
# Schema Yml Tests
#=============================================================================

class TestSchema(unittest.TestCase):
    def test_schema_columns_different(self):
        s1 = schema.Schema()
        t = schema.Table("test")
        t.add_column("col1", "string")
        t.add_column("col2", "int2")
        s1.add_table(t)

        # Create the new schema
        s2 = schema.Schema()
        t = schema.Table("test")
        t.add_column("col1", "string")
        t.add_column("col2", "int")
        s2.add_table(t)

        assert s1 != s2

    def test_schema_equals(self):
        s1 = schema.Schema()
        t = schema.Table("test")
        t.add_column("col1", "string")
        t.add_column("col2", "int")
        s1.add_table(t)
        t = schema.Table("test2")
        t.add_column("col1", "varchar(255)")
        t.add_column("col2", "char")
        s1.add_table(t)

        # Create the new schema
        s2 = schema.Schema()
        t = schema.Table("test")
        t.add_column("col1", "string")
        t.add_column("col2", "int")
        s2.add_table(t)

        assert s1 != s2

        t = schema.Table("test2")
        t.add_column("col1", "varchar(255)")
        t.add_column("col2", "char")
        s2.add_table(t)

        assert s1 == s2


#=============================================================================
# main
#=============================================================================

def main():
    unittest.main()

if __name__ == '__main__':
    main()
