#!/usr/bin/env python
# encoding: utf-8
"""
Created by Jason Rowland on 2012-06-04.
Copyright (c) 2012 Jason Rowland. All rights reserved.
"""

from cStringIO import StringIO

class Table(object):
    def __init__(self):
        self.table = None
        self.columns = list
        self.rows = list
        
    def get_yaml(self, indent=""):
        if not self.rows:
            return None
            
        s = StringIO()
        s.write(indent + self.table.name + ":\n")
        
        # Column Headers
        s.write(indent + "  columns: [" )
        for index in range(len(self.columns)):
            if (index > 0):
                s.write(", ")
            s.write('"' + self.columns[index][0] + '"')
        s.write("]\n")
        
        
        s.write(indent + "  rows:\n")
        # Rows
        for row in self.rows:
            s.write(indent + "    - [")
            for index in range(len(row)):
                if (index > 0):
                    s.write(", ")
                if row[index] == None:
                    s.write('~')
                else:
                    s.write('"%s"' % row[index] )
            s.write("]\n")
    
        return_str = s.getvalue()
        s.close()
        return return_str


class Dataset(object):
    def __init__(self):
        self.tables = None


def main():
    pass

if __name__ == '__main__':
    main()

