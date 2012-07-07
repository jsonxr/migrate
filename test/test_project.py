'''
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
'''


import os
import shutil
import tempfile

import project


def test_project_init():
    """
    Project.init()
    """
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
        shutil.rmtree(path)  # Make sure we clean up after ourselves


def test_project_bootstrap():
    """
    Project.bootstrap()
    """
    path = tempfile.mkdtemp()
    try:
        p = project.Project(path)
        p.init()
        p.bootstrap()
    finally:
        shutil.rmtree(path)  # Make sure we clean up after ourselves
