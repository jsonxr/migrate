import unittest

import database
import schema


#=============================================================================
# DatabaseVersion Tests
#=============================================================================

def test_expected_schema():
    """
    DatabaseVersion: dbversion.expected_schema
    """
    dbversion = database.DatabaseVersion()
    s = schema.Schema()
    s.tables["bob"] = schema.Table("bob")
    dbversion.expected_schema = s
    assert dbversion.expected_schema.tables["bob"]


def test_actual_schema():
    """
    DatabaseVersion: dbversion.actual_schema
    """
    dbversion = database.DatabaseVersion()
    s = schema.Schema()
    s.tables["bob"] = schema.Table("bob")
    dbversion.actual_schema = s
    assert dbversion.actual_schema.tables["bob"]


#=============================================================================
# main
#=============================================================================

def main():
    unittest.main()

if __name__ == '__main__':
    main()
