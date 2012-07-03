import unittest

import schema
import yaml


class SchemaTests(unittest.TestCase):

    def testYamlToVersion(self):
        expected = """
version: ~
hash: c701acfdbf5e70e8d800216cc4df13230e77ff9c
tables:
    - name: test1
      columns:
          - name: col1
            type: string
            key: false
            nullable: true
          - name: col2
            type: string
            key: false
            nullable: true
"""
        expected = expected.strip()

        data = yaml.load(expected)
        v = schema.Version()
        v.load_from_dict(data)
        yml = repr(v)
        assert yml == expected, "yml != expected\n\n%s\n\n%s\n" % (yml, expected)

    def testVersionToYaml(self):
        expected = """
version: ~
hash: c701acfdbf5e70e8d800216cc4df13230e77ff9c
tables:
    - name: test1
      columns:
          - name: col1
            type: string
            key: false
            nullable: true
          - name: col2
            type: string
            key: false
            nullable: true
"""
        expected = expected.strip()
        v = schema.Version()

        t = schema.Table()
        t.name = "test1"
        t.add_column("col1", "string")
        t.add_column("col2", "string")
        v.add_table(t)

        yml = repr(v)
        assert yml == expected, "yml != expected\n\n%s\n\n%s\n" % (yml, expected)

    def testYamlToSchema(self):
        expected = """
tables:
    - name: test1
      columns:
          - name: col1
            type: string
            key: false
            nullable: true
          - name: col2
            type: string
            key: false
            nullable: true
    - name: test2
      columns:
          - name: col1
            type: string
            key: false
            nullable: true
          - name: col2
            type: string
            key: false
            nullable: true
"""
        expected = expected.strip()

        data = yaml.load(expected)
        s = schema.Schema()
        s.load_from_dict(data)
        yml = repr(s)

        assert yml == expected, "yml != expected\n\n%s\n\n%s\n" % (yml, expected)

    def testSchemaToYaml(self):
        expected = """
tables:
    - name: test1
      columns:
          - name: col1
            type: string
            key: false
            nullable: true
          - name: col2
            type: string
            key: false
            nullable: true
"""
        expected = expected.strip()

        s = schema.Schema()
        t = schema.Table()
        t.name = "test1"
        t.add_column("col1", "string")
        t.add_column("col2", "string")
        s.add_table(t)

        yml = repr(s)

        assert yml == expected, "yml != expected\n\n%s\n\n%s\n" % (yml, expected)

    def testYamlToTable(self):
        expected = """
name: testtable
columns:
    - name: col1
      type: string
      key: false
      nullable: true
    - name: col2
      type: string
      key: true
      nullable: false
"""
        expected = expected.strip()

        data = yaml.load(expected)
        t = schema.Table()
        t.load_from_dict(data)
        yml = repr(t)
        assert yml == expected, "yml != expected\n\n%s\n\n%s\n" % (yml, expected)

    def testTableToYaml(self):
        expected = """
name: testtable
columns:
    - name: col1
      type: string
      key: false
      nullable: true
    - name: col2
      type: string
      key: true
      nullable: false
"""
        expected = expected.strip()

        t = schema.Table()
        t.name = "testtable"
        t.add_column("col1", "string")
        c = t.add_column("col2", "string")
        c.nullable = False
        c.key = True
        yml = repr(t)

        assert yml == expected, "\n%s\n != \n%s\n" % (yml, expected)

    def testIndent(self):
        original = """name"""
        result = schema.indent(original)
        expected = """    name"""
        assert expected == result


def main():
    unittest.main()

if __name__ == '__main__':
    main()
