#!/usr/bin/env python
# encoding: utf-8
"""
Created by Jason Rowland on 2012-05-25.
Copyright (c) 2012 Jason Rowland. All rights reserved.
"""
from cStringIO import StringIO
from contextlib import closing
import os
import shutil
import sys
import yaml

import config
from errors import AppError
import database
import schema


#-----------------------------------------------------------------------------
# Helper function
#-----------------------------------------------------------------------------

def _get_resource_path(name):
    resource = os.path.dirname(os.path.realpath(__file__)) + '/resources' + name
    return resource

skeleton = _get_resource_path('/skeleton/')


#-----------------------------------------------------------------------------
# Project
#-----------------------------------------------------------------------------

class Project(object):
    FILENAME = "project.yml"
    OVERRIDES = ".jake"

    def __init__(self, path):
        self.path = path
        self._filename = self.path + "/" + Project.FILENAME
        self.project_settings = None
        self._environment = None
        self.__load_project_file()

    @property
    def environment(self):
        return self._environment

    @environment.setter
    def environment(self, value):
        self._environment = value
        self.connection_info = self.project_settings['environments'][self.environment]

    @property
    def filename(self):
        return self._filename

    @property
    def is_valid(self):
        if self.project_settings is None:
            return False
        else:
            return True

    def __load_project_file(self):
        # project.yml
        if os.path.exists(self.filename):
            with file(self.filename, 'r') as stream:
                self.project_settings = yaml.load(stream)
        # .jake file overrides
        override_yaml = {}
        filename = self.path + "/" + Project.OVERRIDES
        if os.path.exists(filename):
            with file(filename, 'r') as stream:
                override_yaml = yaml.load(stream)
        for key in override_yaml:
            self.project_settings[key].update(override_yaml[key])
        if self.project_settings:
            config.load(self.project_settings)
            # Set the default environment
            if "settings" in self.project_settings and "environment" in self.project_settings["settings"]:
                self.environment = self.project_settings["settings"]["environment"]

    def __ensure_valid(self):
        if not self.is_valid:
            raise AppError('Not a valid repository.  Run init first.')

    def status(self):
        self.__ensure_valid()

        versions = schema.get_versions()

        if versions is None:
            previous = None
            current = None
        else:
            previous = versions.get_previous()
            current = versions.get_current()

        #print(versions.get_from_path())
        #print(current)
        #print(previous)
        #exit()

        # Get the database version
        db = database.get(self.connection_info)
        v = db.get_version()

        #current = version.get_current(self.path)
        #previous = version.get_previous(self.path)

        with closing(StringIO()) as s:

            # On dev04:migrate_dev version:bootstrap
            s.write('# On env={environment}, db={database}, version={version}\n'.format(environment=self.environment, database=self.connection_info["database"], version=v.name))
            if previous is None:
                s.write('#\n')
                if (db.exists()):
                    s.write('#  (use "jake bootstrap" to initialize project with database schema)\n')
                else:
                    s.write('#  (use "jake db-create" to create empty database)\n')
            else:
                s.write('# Schema changes since %s\n' % previous.name)
                s.write('#\n')
                for table_name in current.changeset.tables:
                    commands = current.changeset.tables[table_name]
                    for command_name in commands:
                        command = commands[command_name]
                        s.write('#   {}\n'.format(command.display(current.schema, None)))
                s.write('#\n')
                s.write('#  (use "jake sync" to sync database to schema)\n')
                s.write('#  (use "jake reset HEAD <table>..." to unstage)\n')
            return s.getvalue()

    def init(self):
        if self.is_valid:
            raise AppError('Project has already been initialized')

        # Create the directory if we pass it in.  Don't want to create the
        #
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        for filename in os.listdir(skeleton):
            src = skeleton + filename
            if os.path.isdir(src) == True:
                shutil.copytree(src, self.path + "/" + filename, symlinks=False, ignore=None)
            else:
                shutil.copyfile(src, self.path + "/" + filename)

        return "Edit the project.yaml file to connect to the database."

    def bootstrap(self):
        self.__ensure_valid()
        if os.path.exists('versions/bootstrap.yml'):
            raise AppError("bootstrap can only be run on an empty project without versions.")
        # Create the bootstrap version
        db = database.get(self.connection_info)
        dbversion = db.get_version()
        db_schema = dbversion.actual_schema
        bootstrap_version = self.create_bootstrap(db_schema)
        # Modify the migrations table to honor the migration_table setting.
        migration_table = schema.Table()
        migration_table.load_from_file(_get_resource_path('/migrations.yml'))
        migration_table.name = config.migration_table
        # Create the current schema
        current = schema.Version()
        current.filename = self.path + "/versions/current.yml"
        current.name = "current"
        current.schema = bootstrap_version.schema
        current.migration.previous = bootstrap_version.name
        current.create_table(migration_table)
        # Save the current version to the path and the current.yml
        current.save_to_file()
        current.save_to_path(self.path + "/schema")

    def create_bootstrap(self, dbschema):
        os.makedirs(self.path + '/versions')
        b = schema.Version()
        b.filename = self.path + "/versions/bootstrap.yml"
        b.name = 'bootstrap'
        b.schema = dbschema
        b.save_to_file()
        return b

    def add(self):
        pass

    def reset(self):
        pass

    def rm(self):
        pass

#
#    def status2(self):
#        self.__ensure_valid()
#        db = database.get(self.connection_info)
#        current = version.get_previous(self.path)
#        db_schema = db.schema
#        yml_schema = self.__load_yml_schema()
#
#        try:
#            if db_schema is None:
#                print "# On first version"
#                print "Database does not exist. type jake db-create to create `%s`." % db.database
#            else:
#                print "# On schema version \"%s+\"" % current.name
#                print "# On database=\"%s\" version=\"%s\"" % (db.database, db_schema.version)
#
#                cs = changeset.Changeset()
#                cs.load(self.path + "/versions/current.yaml")
#
#                # Changes since last version
#                last_schema = schema.load_from_file("versions/" + current.filename)
#                version_cs = changeset.diff(cs, yml_schema, last_schema)
#                # if not version_cs.is_empty():
#                #     print("# Changes since last version:")
#                #     print("#")
#                #     version_cs.display()
#                #     sys.stdout.write("\033[0m")
#
#                if not cs.is_empty():
#                    print("# Changes to sync:")
#                    print("#   (use \"jake reset <table>...\" to unstage)")
#                    print("#")
#                    cs.display()
#                    sys.stdout.write("\033[0m")
#                #exit()
#
#                cs = changeset.diff(cs, yml_schema, db_schema)
#                if not cs.is_empty():
#
#                    #
#                    # Changed but not updated:
#                    #   (use "git add <file>..." to update what will be committed)
#                    #   (use "git checkout -- <file>..." to discard changes in working directory)
#                    #
#                    #    modified:   test2.yaml
#                    #
#                    print("#")
#                    print("# Changed but won't be synced:")
#                    print("#   (use \"jake add <table>...\" to update what will be committed")
#                    print("#")
#                    cs.display()
#                    sys.stdout.write("\033[0m")
#
#                print("no changes added to commit (use \"git add\" and/or \"git commit -a\")")
#        finally:
#            sys.stdout.write("\033[0m")

    def sync(self):
        self.__ensure_valid()
        db = database.get(self.connection_info)
        #db_schema = db.schema
        #yml_schema = self.__load_yml_schema()

        cs = None
        yml_schema = None
        #cs = changeset.Diff(self.path + "/versions/current.yaml", yml_schema, db_schema)
        db.sync(cs, yml_schema)

    def db_create(self):
        self.__ensure_valid()
        db = database.get(self.connection_info)
        db_schema = db.create()
        return db_schema

    def db_drop(self):
        self.__ensure_valid()
        db = database.get(self.connection_info)
        db.drop()

    def dump(self, name=None):
        self.__ensure_valid()

        yml = self.__dump(name)
        if yml:
            print yml
        else:
            print "(database is empty)"

    def __dump(self, name=None):
        db = database.get(self.connection_info)
        db_schema = db.schema
        if (name):
            table = db_schema.get_table(name)
            yml = "tables:\n" + table.get_yaml()
        else:
            yml = db_schema.get_yaml()
        return yml

    def load_dataset(self, filename):
        pass

    def list_versions(self):
        versions = schema.get_versions()
        if (versions):
            print
            for version in versions:
                print "%s => %s" % (version.name, version.filename)
        else:
            print "Need to either run bootstrap or version create."

    def save_dataset(self, filename):
        self.__ensure_valid()
        db = database.get(self.connection_info)
        db_dataset = db.get_dataset()
        print db_dataset


def main(argv=None):
    pass

if __name__ == "__main__":
    sys.exit(main())
