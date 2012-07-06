import unittest

import re


#=============================================================================
# Schema Yml Tests
#=============================================================================

def map_type(field_type):
    #_compiled_re = re.compile('^(?P<all>.*)$', re.MULTILINE)

    #print('before: [%s]' % strings)
    #newstr = _compiled_re.sub('\g<all>', strings.rstrip())

    #- search: ^varchar\((?P<limit>\d*)\)$
    #  replace: string(\g<limit>)
      
    _compiled_re = re.compile("^dec\((?P<n>[\d,]*)\)")
    newstr = _compiled_re.subn('decimal(\g<n>)', field_type)
    return newstr


class FunctionTests(unittest.TestCase):

    def test_mysql_mappings(self):
        print(map_type("dec(10,2) unsigned"))


#=============================================================================
# main
#=============================================================================

def main():
    unittest.main()

if __name__ == '__main__':
    main()
