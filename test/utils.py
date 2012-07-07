'''
Created by Jason Rowland on 2012-05-28.
Copyright (c) 2012 Jason Rowland. All rights reserved.
'''
from _mysql_exceptions import MySQLError
import MySQLdb
import os
import yaml

import db_mysql

#-----------------------------------------------------------------------------
# Test settings for mysql
#-----------------------------------------------------------------------------

filename = os.path.dirname(os.path.realpath(__file__)) + '/.databases.yml'
with file(filename) as stream:
    data = yaml.load(stream)
DB_HOST = data["mysql"]["host"]
DB_USER = data["mysql"]["user"]
DB_PASSWORD = data["mysql"]["password"]
DB_DATABASE = data["mysql"]["database"]


#-----------------------------------------------------------------------------
# Helper functions
#-----------------------------------------------------------------------------

def get_resource_filename(path):
    filename = os.path.dirname(os.path.realpath(__file__)) + "/resources" + path
    return filename


def get_resource(path):
    filename = get_resource_filename(path)
    with file(filename, 'r') as stream:
        return stream.read().strip()


def read_from_file(path):
    with file(path, 'r') as stream:
        return stream.read().strip()


def database_exists():
    try:
        conn = MySQLdb.connect(host=DB_HOST, user=DB_USER,
                passwd=DB_PASSWORD, db=DB_DATABASE)
        conn.close()
        return True
    except MySQLError as e:
        if (e[0] == db_mysql.ER_BAD_DB_ERROR):
            return False
        else:
            raise


def get_database():
    connection = {"host": DB_HOST, "database": DB_DATABASE, "user": DB_USER, "password": DB_PASSWORD}
    db = db_mysql.Database(connection)
    return db


def assert_yml_equal(yml, expected):
    # Covert to dict
    yml_dict = yaml.load(yml)
    exp_dict = yaml.load(expected)
    assert yml_dict == exp_dict, "yml != expected\n\n[%s]\n\n[%s]\n" % (yml, expected)
#    # Convert to yml because this allows us to write yml of different styles
#    # But still allow them to compare true
#    yml = yaml.dump(yml_dict, default_flow_style=False)
#    expected = yaml.dump(exp_dict, default_flow_style=False)
#    print(yml)
#    print(expected)
#    assert yml == expected, "yml != expected"
