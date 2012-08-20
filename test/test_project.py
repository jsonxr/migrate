'''
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
'''
import unittest

import project
import fixtures


#-----------------------------------------------------------------------------
# Test settings for mysql
#-----------------------------------------------------------------------------

class TestProject(unittest.TestCase):

    def test_project_init(self):
        with fixtures.TestFixture() as tf:
            p = project.Project(tf.temp_path)
            p.init()
            tf.assert_directory(project.skeleton, p.path)

    def test_project_bootstrap_emptydb(self):
        with fixtures.TestFixture("bootstrap_emptydb") as tf:
            p = project.Project(tf.temp_path)
            p.init()
            assert_dir = tf.get_assert_filename('/test_project/bootstrap_emptydb')
            tf.assert_directory(assert_dir, p.path)

    def test_project_bootstrap_emptydb_status(self):
        with fixtures.TestFixture("head_emptydb", clean=True) as tf:
            p = project.Project(tf.temp_path)
            print(p.status())


#-----------------------------------------------------------------------------
# main
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
