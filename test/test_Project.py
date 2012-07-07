'''
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
'''


import os
import shutil
import tempfile
import unittest

import project
import utils


#-----------------------------------------------------------------------------
# Test settings for mysql
#-----------------------------------------------------------------------------

class TestProject(unittest.TestCase):
    def test_project_init(self):
        path = tempfile.mkdtemp()
        try:
            p = project.Project(path)
            p.init()
            assert os.path.exists(p.filename)
            assert os.path.exists(path + "/project.yml")
            assert os.path.exists(path + "/readme.txt")
            assert os.path.exists(path + "/schema/changes.yml")
            assert os.path.exists(path + "/schema/tables/readme.txt")
            assert os.path.exists(path + "/schema/procedures/readme.txt")
            assert os.path.exists(path + "/versions/readme.txt")
        finally:
            #print(path)
            shutil.rmtree(path)  # Make sure we clean up after ourselves

    def test_project_bootstrap(self):
        path = tempfile.mkdtemp()
        try:
            p = project.Project(path)
            p.init()
            # Create a temporary database
            db = utils.get_database()
            db.execute_create()
            # Edit the project.yml file
            params = (utils.DB_HOST, utils.DB_DATABASE, utils.DB_USER, utils.DB_PASSWORD)
            project_file = YML_TEST_PROJECT % params
            with file(p.filename, 'w') as stream:
                stream.write(project_file)
            # We need to reload the project because we've changed the project file
            # Since when in use we edit the project.yml file in between init and
            # bootstrap, the project is reloaded right before bootstrap
            p = project.Project(path)
            p.bootstrap()
        finally:
            db.execute_drop()
            shutil.rmtree(path)  # Make sure we clean up after ourselves


#-----------------------------------------------------------------------------
# Resources
#-----------------------------------------------------------------------------
YML_TEST_PROJECT = utils.get_resource("/test_project.yml")


#-----------------------------------------------------------------------------
# main
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
