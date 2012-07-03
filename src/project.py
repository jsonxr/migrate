#!/usr/bin/env python
# encoding: utf-8
"""
Created by Jason Rowland on 2012-05-25.
Copyright (c) 2012 Jason Rowland. All rights reserved.
"""

import os
import shutil
import sys
import yaml

import config
from errors import AppError

import database
import schema


class Project(object):
    FILENAME = "project.yml"
    OVERRIDES = ".jake"

    # def __call__(self, parser, namespace, values, option_string=None):
    #     print('%r %r %r' % (namespace, values, option_string))
    #     #setattr(namespace, self.dest, values)

    def __init__(self):
        self.path = os.path.abspath(".")
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

    def __load_project_file(self):
        filename = self.path + "/" + Project.FILENAME
        if os.path.exists(filename):
            stream = file(filename, 'r')
            self.project_settings = yaml.load(stream)
            stream.close()

        # Override main key values
        override_yaml = {}
        filename = self.path + "/" + Project.OVERRIDES
        if os.path.exists(filename):
            stream = file(filename, 'r')
            override_yaml = yaml.load(stream)
            stream.close()
        for key in override_yaml:
            self.project_settings[key].update(override_yaml[key])

        if self.project_settings:
            config.load(self.project_settings)
            # Set the default environment
            if "settings" in self.project_settings and "environment" in self.project_settings["settings"]:
                self.environment = self.project_settings["settings"]["environment"]

    def is_valid(self):
        if self.project_settings is None:
            return False
        else:
            return True

    def __ensure_valid(self):
        if not self.is_valid():
            raise AppError('Not a valid repository.  Run init first.')

    def status(self):
        self.__ensure_valid()

        versions = schema.get_versions()
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

        # On dev04:migrate_dev version:bootstrap
        print('# On env={environment}, db={database}, version={version}'.format(environment=self.environment, database=self.connection_info["database"], version=v.name))

        if previous is None:
            print('#')
            if (db.exists()):
                print('#  (use "jake bootstrap" to initialize project with database schema)')
            else:
                print('#  (use "jake db-create" to create empty database)')
        else:
            print('# Schema changes since %s' % previous.name)
            print('#')
            for table_name in current.changeset.tables:
                commands = current.changeset.tables[table_name]
                for command_name in commands:
                    command = commands[command_name]
                    print('#   {}'.format(command.display(current.schema, None)))
            print('#')
            print('#  (use "jake sync" to sync database to schema)')
            print('#  (use "jake reset HEAD <table>..." to unstage)')

    def init(self):
        if self.is_valid():
            raise AppError('Project has already been initialized')

        # Create the directory if we pass it in.  Don't want to create the
        #
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        skeleton = self.__getResourcePath('/skeleton/')
        for filename in os.listdir(skeleton):
            src = skeleton + filename
            if os.path.isdir(src) == True:
                shutil.copytree(src, self.path + "/" + filename, symlinks=False, ignore=None)
            else:
                shutil.copyfile(src, self.path + "/" + filename)

        print("Edit the project.yaml file to connect to the database.")

    def bootstrap(self):
        self.__ensure_valid()

        if os.path.exists('versions/bootstrap.yml'):
            raise AppError("bootstrap can only be run on an empty project without versions.")

        # Create the bootstrap version
        db = database.get(self.connection_info)
        db_schema = db.get_db_schema()
        bootstrap_version = schema.create_bootstrap(db_schema)

        # Save all the schema
        changelog_table = schema.Table()
        changelog_table.load_from_file(self.__getResourcePath('/changelog.yml'))
        changelog_table.name = config.changelog

        db_schema.add_table(changelog_table)
        #print(db_schema)
        db_schema.save_to_path(self.path + "/schema")
#
#        # Create the versions/index file.
#        with file('versions/index.yml', 'w') as f:
#            f.write('# Version index file.')
#            f.write('versions:\n')
#            f.write('    - %s:\n' % bootstrap_version.name)
#            f.write('        filename: "%s"\n' % bootstrap_version.filename)
#            f.write('        hashcode: "%s"' % bootstrap_version.hashcode)

        current = bootstrap_version
        current.name = "current"
        current.filename = "current.yml"
        current.add_table(changelog_table)
        current.save()

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
#                print "#        hashcode=\"%s\"" % yml_schema.get_hash()
#                print "#    previous=\"%s\"" % current.hashcode
#                print "# On database=\"%s\" version=\"%s\"" % (db.database, db_schema.version)
#                print "#        hashcode=\"%s\"" % db_schema.get_hash()
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

    def __getResourcePath(self, name):
        resource = os.path.dirname(os.path.realpath(__file__)) + '/resources' + name
        return resource


def main(argv=None):
    pass

if __name__ == "__main__":
    sys.exit(main())
