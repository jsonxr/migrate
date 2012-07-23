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
    OVERRIDES = ".db"

    def __init__(self, path):
        self.path = path
        self._filename = self.path + "/" + Project.FILENAME
        self.project_settings = None
        self._environment = None
        self._versions = None
        self._db = None
        # The different versions
        self._bootstrap_version = None
        self._path_version = None
        self._head_version = None
        self._expected_version = None
        self._actual_version = None
        self.__load_project_file()

    @property
    def db(self):
        if self._db is None:
            self._db = database.get(self.connection_info)
        return self._db

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
    def versions(self):
        if self._versions is None:
            self._versions = schema.Versions(self.path)
        print (self._versions)
        return self._versions

    @property
    def head_version(self):
        if self._head_version is None:
            self._head_version = self.versions.get_head()
        print(self._head_version)
        return self._head_version

    @property
    def bootstrap_version(self):
        if self._bootstrap_version is None:
            self._bootstrap_version = self.versions.get_bootstrap()
        print(self._bootstrap_version)
        return self._bootstrap_version

    @property
    def expected_version(self):
        if self._expected_version is None:
            self._expected_version = self.db.get_expected_version()
            if self._expected_version is None:
                self._expected_version = self.bootstrap_version
        print(self._expected_version)
        return self._expected_version

    @property
    def is_valid(self):
        if self.project_settings is None:
            return False
        else:
            if self.head_version is None:
                return False
            else:
                return True

    def __load_project_file(self):
        # project.yml
        if os.path.exists(self.filename):
            with file(self.filename, 'r') as stream:
                self.project_settings = yaml.load(stream)
        # .db file overrides
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
            self.connection_info = self.project_settings['environments'][self.environment]

    def __ensure_valid(self):
        if not self.is_valid:
            raise AppError('Not a valid repository.  Run "db init" first.')

    def status(self):
        print("Project.status:1")
        self.__ensure_valid()

        # Get all the versions
        #previous = self.versions.get_previous(self.head_version)
        #dbversion = self.db.get_version(previous)
        # Write the output
        print("Project.status:2")
        with closing(StringIO()) as s:
            print("Project.status:3")
            if self.expected_version:
                print("Project.status:4")
                s.write('# On env={environment}, db={database}, version={version}\n'.format(environment=self.environment, database=self.connection_info["database"], version=self.expected_version.name))
            else:
                print("Project.status:5")
                s.write('# On env={environment}, db={database}, version=None\n'.format(environment=self.environment, database=self.connection_info["database"]))
            if self.head_version is None:
                print("Project.status:6")
                s.write('#\n')
                if (self.db.exists()):
                    print("Project.status:7")
                    s.write('#  (use "db bootstrap" to initialize project with database schema)\n')
                else:
                    s.write('#  (use "db db-create" to create empty database)\n')
            else:
                print("Project.status:8")
                self._status_changes_to_sync(s)
                self._status_changes_not_added(s)
                self._status_changes_in_database(s)
                print("Project.status:9")
            return s.getvalue()

    def _status_changes_to_sync(self, s):
        # These are the changes that are in the commands list
        # print(dbversion.is_syncable)
        s.write('# Changes to sync to database:\n')
        s.write('#   (use "db undo <table>..." to undo change to database)\n')
        s.write('#   (use "db sync [--force]" to sync database to schema)\n')
        s.write('#\n')
#        for table_name in head_version.migration.tables:
#            commands = head_version.migration.tables[table_name]
#            for command in commands:
#                if command.name == "create_table":
#                    if dbversion.actual_schema.tables[table_name] is None:
#                        s.write('#   {}\n'.format(command.display(sync=True)))
#                    else:
#                        if not head_version.schema.tables[table_name] == dbversion.actual_schema.tables[table_name]:
#                            s.write('#   {}\n'.format(command.display(force=True)))
#                        else:
#                            # They are the same, so it doesn't need to be synced at all
#                            pass
#                elif command.name == "drop_table":
#                    pass
        s.write('#\n')

    def _status_changes_not_added(self, s):
        # These are the changes that are in the path, but are NOT in the head.yml file
        # This includes changes to the path migration.yml file (for example a rename intead of drop/create
        s.write('# Changed in directory but not added to sync:\n')
        s.write('#   (use "db add/drop/rename <table>..." to update what will sync)\n')
        s.write('#   (use "db undo <table>..." to undo change in directory)\n')
        s.write('#\n')
        s.write('# \033[31m{}\033[0m\n'.format('          new table:    test2'))
        s.write('#\n')

    def _status_changes_in_database(self, s):
        s.write('# Changed in database but not in project:\n')
        s.write('#   (use "db reverse <table>..." to save changes to directory)\n')
        s.write('#\n')
        s.write('# \033[31m{}\033[0m\n'.format('          new table:    test1'))
        s.write('#\n')

    def init(self):
        if self.is_valid:
            raise AppError('Project has already been initialized')
        if self.project_settings is None:
            self.create_folders()
            return 'Edit the project.yaml file for your database and rerun "db init"'
        else:
            self.bootstrap()
            return 'The schema from the "%s" database is located in the "schema" directory.' % self.db.database

    def create_folders(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        for filename in os.listdir(skeleton):
            src = skeleton + filename
            if os.path.isdir(src) == True:
                shutil.copytree(src, self.path + "/" + filename, symlinks=False, ignore=None)
            else:
                shutil.copyfile(src, self.path + "/" + filename)

    def bootstrap(self):
        if os.path.exists('versions/bootstrap.yml'):
            raise AppError("bootstrap can only be run on an empty project without versions.")
        # Create the bootstrap version
        db = database.get(self.connection_info)
        db_schema = db.get_actual_schema()
        bootstrap_version = self.create_bootstrap(db_schema)
        # Modify the migrations table to honor the migration_table setting.
        migration_table = schema.Table()
        migration_table.load_from_file(_get_resource_path('/migrations.yml'))
        migration_table.name = config.migration_table
        # Create the head_version schema
        head_version = schema.Version()
        head_version.filename = self.path + "/versions/head.yml"
        head_version.name = "head"
        head_version.schema = bootstrap_version.schema
        head_version.migration.previous = bootstrap_version.name
        head_version.create_table(migration_table)
        # Save the head version to the path and the head.yml
        head_version.save_to_file()
        head_version.save_to_path(self.path + "/schema")

    def create_bootstrap(self, dbschema):
        if not os.path.exists(self.path + '/versions'):
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
#        head = version.get_previous(self.path)
#        db_schema = db.schema
#        yml_schema = self.__load_yml_schema()
#
#        try:
#            if db_schema is None:
#                print "# On first version"
#                print "Database does not exist. type db db-create to create `%s`." % db.database
#            else:
#                print "# On schema version \"%s+\"" % head.name
#                print "# On database=\"%s\" version=\"%s\"" % (db.database, db_schema.version)
#
#                cs = changeset.Changeset()
#                cs.load(self.path + "/versions/head.yaml")
#
#                # Changes since last version
#                last_schema = schema.load_from_file("versions/" + head.filename)
#                version_cs = changeset.diff(cs, yml_schema, last_schema)
#                # if not version_cs.is_empty():
#                #     print("# Changes since last version:")
#                #     print("#")
#                #     version_cs.display()
#                #     sys.stdout.write("\033[0m")
#
#                if not cs.is_empty():
#                    print("# Changes to sync:")
#                    print("#   (use \"db reset <table>...\" to unstage)")
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
#                    print("#   (use \"db add <table>...\" to update what will be committed")
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
        #cs = changeset.Diff(self.path + "/versions/head.yaml", yml_schema, db_schema)
        db.sync(cs, yml_schema)

    def db_create(self):
        if not self.project_settings is None:
            db = database.get(self.connection_info)
            db_schema = db.execute_create()
            return db_schema

    def db_drop(self):
        if not self.project_settings is None:
            db = database.get(self.connection_info)
            db.execute_drop()

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
        versions = schema.Versions()
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
