'''
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
'''
import datetime
import os
import shutil
import tempfile
import yaml

import db_mysql

#-----------------------------------------------------------------------------
# Resource functions
#-----------------------------------------------------------------------------


def read_from_file(filename):
    with file(filename, 'r') as stream:
        return stream.read().strip()


#-----------------------------------------------------------------------------
# Database functions
#-----------------------------------------------------------------------------

# MySQL settings for unit testing
filename = os.path.dirname(os.path.realpath(__file__)) + '/.databases.yml'
with file(filename) as stream:
    data = yaml.load(stream)
DB_HOST = data["mysql"]["host"]
DB_USER = data["mysql"]["user"]
DB_PASSWORD = data["mysql"]["password"]
DB_DATABASE = data["mysql"]["database"]


class TestVersion(object):
    """
    This is responsible for initializing the project to the known state

    testversion.assert_project()
    ----------------------------
    will make sure that all files in the assert
    directory match the project directory.

    testversion.assert_yml_equals(yml, assertfilename)
    --------------------------------------------------
    Compares the yml with a file from the assert directory.  The files
    themselves don't have to match, but the dictionary that they create needs
    to match.
    """
    def __init__(self, name=None):
        self.name = name
        conn = {"host": DB_HOST, "database": DB_DATABASE, "user": DB_USER, "password": DB_PASSWORD}
        self.db = db_mysql.Database(conn)
        self.temp_path = tempfile.mkdtemp()  # This is just to get a tmpdir name
        if name:
            self.testversion_path = os.path.dirname(os.path.realpath(__file__)) + "/testversions/%s" % name
            assert os.path.exists(self.testversion_path), "%s does not exist" % self.testversion_path

    def __enter__(self):
        self.execute()
        return self

    def __exit__(self, exec_type, exec_value, traceback):
        self.clean()

    def get_assert_filename(self, filename):
        assert_filename = os.path.dirname(os.path.realpath(__file__)) + "/assert%s" % filename
        return assert_filename

    def get_assert_file(self, filename):
        assert_filename = self.get_assert_filename(filename)
        return read_from_file(assert_filename).strip()

    def get_filename(self, filename):
        resource_filename = self.testversion_path + filename
        return resource_filename

    def get_resource(self, filename):
        resource_filename = self.testversion_path + filename
        if os.path.exists(resource_filename):
            with file(resource_filename, 'r') as stream:
                return stream.read().strip()
        else:
            return None

    def execute(self):
        if self.name:
            self.__create_project()
            self.__create_database()

    def __create_project(self):
        # Make the project directory
        project_path = self.testversion_path + "/project"
        if os.path.exists(project_path):
            # Clone the project setup to a temp location
            shutil.rmtree(self.temp_path)
            shutil.copytree(project_path, self.temp_path, symlinks=False, ignore=None)
            # Edit the project.yml file
            filename = self.temp_path + "/project.yml"
            if os.path.exists(filename):
                project_file = read_from_file(filename)
                project_file = project_file % (DB_HOST, DB_DATABASE, DB_USER, DB_PASSWORD)
                with file(filename, 'w') as stream:
                    stream.write(project_file)

    def __create_database(self):
        # Make the database structure what we need
        sql = self.get_resource("/mysql.sql")
        if sql:
            self.db.execute_create()
            self.db.execute(sql)
            # Create migrations entries
            migration_versions = self.get_resource('/migration_versions.yml')
            if migration_versions:
                values = []
                data = yaml.load(migration_versions)
                for v in data:
                    name = v["name"]
                    filename = v["filename"]
                    yml = self.get_resource("/%s" % filename)
                    values.append([name, yml, 'unittest', datetime.datetime.now()])
                if values:
                    sql = "INSERT INTO migrations (version, yml, applied_by, applied_on) values (%s,%s,%s,%s)"
                    self.db.execute_many(sql, values)

    def assert_yml_equal(self, yml, filename):
        expected = self.get_assert_file(filename)
        assert expected, "assert file %s does not exist." % (self.testversion_path + '/assert/%s' % filename)
        # Covert to dict
        assert_yml_equal(yml, expected)

    def assert_directory(self, src, dest, base="/"):
        # Make certain that every file in the assert directory
        # matches a file in the project directory.
        for filename in os.listdir(src + base):
            project_filename = '%s%s' % (dest + base, filename)
            compareto = src + base + filename
            if os.path.isdir(project_filename) == True:
                self.assert_directory(src, dest, '%s%s/' % (base, filename))
            else:
                ext = os.path.splitext(project_filename)
                project_file = read_from_file(project_filename)
                assert_file = read_from_file(compareto)
                if ext[1] == ".yml":
                    assert_yml_equal(project_file, assert_file)
                else:
                    assert project_file == assert_file, 'project != assert (%s)\n\n[%s]\n\n[%s]\n' % (
                            base + filename, project_file, assert_file)

    def clean(self):
        if self.db.exists():
            self.db.execute_drop()
        if self.temp_path:
            shutil.rmtree(self.temp_path)


def assert_yml_equal(yml, exp):
    # Convert to yml because this allows us to write yml of different styles
    # But still allow them to compare true
    yml_dict = yaml.load(yml)
    exp_dict = yaml.load(exp)
    assert yml_dict == exp_dict, "yml != expected\n\n[%s]\n%s\n\n[%s]\n%s\n" % (yml_dict, yml, exp_dict, exp)
