'''
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
'''
import glob
import os
import shutil
import sys
import tempfile
import yaml

import db_mysql


#-----------------------------------------------------------------------------
# Resource functions
#-----------------------------------------------------------------------------

def read_from_file(filename):
    with file(filename, 'r') as stream:
        return stream.read().strip()


def get_file_contents(filename):
    if os.path.exists(filename):
        return read_from_file(filename)
    else:
        return None


def _sandbox_eval(string):
    #make a list of safe functions
    safe_list = ['math', 'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos',
                 'cosh', 'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod',
                 'frexp', 'hypot', 'ldexp', 'log', 'log10', 'modf', 'pi',
                 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh']
    #use the list to filter the local namespace
    safe_dict = dict([(k, locals().get(k, None)) for k in safe_list])
    #add any needed builtins back in.
    safe_dict['abs'] = abs
    return eval(string, {"__builtins__": None, "datetime": sys.modules['datetime']}, safe_dict)


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


class TestFixture(object):
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
    def __init__(self, name=None, clean=True):
        self.name = name
        self.clean_when_finished = clean
        conn = {"host": DB_HOST, "database": DB_DATABASE, "user": DB_USER, "password": DB_PASSWORD}
        self.db = db_mysql.Database(conn)
        self.temp_path = tempfile.mkdtemp()  # This is just to get a tmpdir name
        if name:
            self.testversion_path = os.path.dirname(os.path.realpath(__file__)) + "/fixtures/%s" % name
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
        return get_file_contents(resource_filename)

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
            path = self.get_filename('/data/*.yml')
            for filename in glob.glob(path):
                self.__load_data(filename)

    def __load_data(self, filename):
        # Create migrations entries
        datafile = get_file_contents(filename)
        if datafile:
            data = yaml.load(datafile)
            values = data["values"]
            # Load from filename if we have an object
            for row in values:
                for i in range(len(row)):
                    field = row[i]
                    if type(field) is dict:
                        if "filename" in field:
                            row[i] = self.get_resource(field["filename"])
                        elif "eval" in field:
                            row[i] = _sandbox_eval(field["eval"])
            sql = data["sql"]
            self.db.execute_many(sql, values)

    def assert_yml_equal_str(self, yml, exp):
        # Convert to yml because this allows us to write yml of different styles
        # But still allow them to compare true
        try:
            yml_dict = yaml.load(yml)
            exp_dict = yaml.load(exp)
            assert yml_dict == exp_dict, "yml != expected\n\n[%s]\n%s\n\n[%s]\n%s\n" % (yml_dict, yml, exp_dict, exp)
        except yaml.scanner.ScannerError as e:
            assert False, 'invalid yml \n\n[%s]\n\n%s' % (yml, str(e))

    def assert_yml_equal_file(self, yml, filename):
        expected = self.get_assert_file(filename)
        assert expected, "assert file %s does not exist." % (self.testversion_path + '/assert/%s' % filename)
        # Covert to dict
        self.assert_yml_equal_str(yml, expected)

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
                yml = read_from_file(project_filename)
                exp = read_from_file(compareto)
                if ext[1] == ".yml":
                    yml_dict = yaml.load(yml)
                    exp_dict = yaml.load(exp)
                    assert yml_dict == exp_dict, "yml != expected\n\n%s\n[%s]\n%s\n\n%s\n[%s]\n%s\n" % (yml_dict, project_filename, yml, compareto, exp_dict, exp)
                else:
                    assert yml == exp, 'project != assert (%s)\n\n[%s]\n\n[%s]\n' % (
                            base + filename, yml, exp)

    def clean(self):
        if self.clean_when_finished:
            if self.name and self.db.exists():
                self.db.execute_drop()
            if self.temp_path:
                shutil.rmtree(self.temp_path)
        else:
            print('manually delete %s' % self.temp_path)
