'''
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
'''
import fixtures
import unittest
import os
import yaml_cache

import schema


#=============================================================================
# Table
#=============================================================================

class TestYamlCache(unittest.TestCase):
    def test_save_cache(self):
        with fixtures.TestFixture("head_test1test2") as tf:
            project_path = tf.temp_path
            filename = "/versions/head.yml"
            expected = schema.Version()
            expected.load_from_file(project_path + filename)
            cached = yaml_cache.load(project_path, filename, schema.Version)
            assert cached == expected
            assert os.path.exists(project_path + "/.cache" + filename)


#=============================================================================
# main
#=============================================================================

def main():
    unittest.main()

if __name__ == '__main__':
    main()
