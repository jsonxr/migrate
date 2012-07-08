'''
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
'''
import unittest

import project
import utils


#-----------------------------------------------------------------------------
# Test settings for mysql
#-----------------------------------------------------------------------------

class TestProject(unittest.TestCase):

    def test_project_init(self):
        with utils.TestVersion() as tv:
            p = project.Project(tv.temp_path)
            p.init()
            tv.assert_directory(project.skeleton, p.path)

    def test_project_bootstrap_emptydb(self):
        with utils.TestVersion("bootstrap_emptydb") as tv:
            p = project.Project(tv.temp_path)
            p.bootstrap()
            assert_dir = tv.get_assert_filename('/test_project/bootstrap_emptydb')
            tv.assert_directory(assert_dir, p.path)


#-----------------------------------------------------------------------------
# main
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
