'''
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
'''
import fixtures
import unittest
import os
import cache

import schema


#=============================================================================
# Table
#=============================================================================

class TestYamlCache(unittest.TestCase):
    def test_save_cache(self):
        with fixtures.TestFixture("head_test1test2", clean=True) as tf:
            project_path = tf.temp_path
            filename = "/versions/head.yml"
            expected = schema.Version()
            content = fixtures.read_from_file(project_path + filename)
            expected.load_from_str(content)
            cached = cache.load(project_path, filename, schema.Version)
            assert cached == expected
            print(project_path + "/.cache" + filename)
            assert os.path.exists(project_path + "/.cache" + filename + ".pickle")


#=============================================================================
# main
#=============================================================================

def main():
    unittest.main()

if __name__ == '__main__':
    main()
