#!/usr/bin/env python
# encoding: utf-8
"""
Created by Jason Rowland on 2012-05-25.
Copyright (c) 2012 Jason Rowland. All rights reserved.
"""
from cStringIO import StringIO
from contextlib import closing
import sys

import schema

#-----------------------------------------------------------------------------
# Helper function
#-----------------------------------------------------------------------------
RED = "\033[31m{}\033[0m"
GREEN = "\033[32m{}\033[0m"
YELLOW = "\033[33m{}\033[0m"


def get_status(project):
    # Get all the versions
    print("bootstrap----------------------")
    bootstrap = project.bootstrap_version
    print(bootstrap)

    print("previous-----------------------")
    previous = project.versions.get_previous(project.head_version)
    print(previous)

    print("expected-----------------------")
    expected = project.expected_version
    print(expected)

    print("pathversion--------------------")
    pathVersion = project.path_version
    print(pathVersion)

    print("actual-------------------------")
    actual = project.actual_schema
    print(actual)

    print("head---------------------------")
    head = project.head_version
    print(head)
    #dbversion = project.db.get_version(previous)
    # Write the output
    with closing(StringIO()) as s:
        if project.expected_version:
            ename = project.expected_version.name
        else:
            ename = 'None'
        s.write('# On env={environment}, db={database}, version={version}\n'.format(environment=project.environment,
                        database=project.connection_info["database"], version=ename))
        if project.head_version is None:
            s.write('#\n')
            if (project.db.exists()):
                s.write('#  (use "db bootstrap" to initialize project with database schema)\n')
            else:
                s.write('#  (use "db db-create" to create empty database)\n')
        else:
            changes_to_sync = get_status_changes_to_sync(project)
            if changes_to_sync:
                s.write(changes_to_sync)
            changes_not_added = get_status_changes_not_added(project)
            if changes_not_added:
                s.write(changes_not_added)

            #project._status_changes_not_added(s)
            #project._status_changes_in_database(s)
            #print("Project.status:9")
            pass
        return s.getvalue()


#    def display(self):
#        _format_str = RED
#        _format_str = GREEN
#        if sync:
#            _sync = "[sync]"
#        if force:
#            _sync = "[force]"
#        s = "{:7} {:13} {:20}".format(_sync, "new table:", self.table)
#        return "{}".format(_format_str.format(s))

def get_status_changes_to_sync(project):
    head_tables = project.head_version.schema.tables
    actual_tables = project.actual_schema.tables

    if head_tables == actual_tables:
        return None

    expected_tables = project.expected_version.schema.tables

    # These are the changes that are in the commands list
    # print(dbversion.is_syncable)
    with closing(StringIO()) as s:
        for table_name in project.head_version.migration.tables:
            actual_table = actual_tables[table_name]
            expected_table = expected_tables[table_name]
            head_table = head_tables[table_name]

            syncable = actual_table == expected_table
            needs_sync = head_table != actual_table
            if needs_sync and syncable:
                cmd_array = project.head_version.migration.tables[table_name].commands
                print('cmd_array')
                print(cmd_array)
                s.write(get_commands_display(table_name, cmd_array, actual_table, expected_table, head_table, GREEN))
        s.write('#\n')
        syncable = s.getvalue()
    if syncable:
        with closing(StringIO()) as s:
            s.write('# Changes to sync to database:\n')
            s.write('#   (use "db undo <table>..." to undo change to database)\n')
            s.write('#   (use "db sync [--force]" to sync database to schema)\n')
            s.write('#\n')
            s.write(syncable)
            return s.getvalue()
    else:
        return None


def get_commands_display(table_name, cmd_array, actual_table, expected_table, head_table, color):
    with closing(StringIO()) as s:
        for cmd_name in cmd_array:
            cmd = cmd_array[cmd_name]
            cmd_display = "{:13}   {:20}".format(cmd.display + ':', cmd.table_name)
            s.write('#       %s\n' % color.format(cmd_display))
        return s.getvalue()


def get_status_changes_not_added(project):
    # Do we even need to do this?
    head_tables = project.head_version.schema.tables
    path_tables = project.path_version.schema.tables
    if path_tables == head_tables:
        return None

    #actual_tables = project.actual_schema.tables
    #expected_tables = project.expected_version.schema.tables

    with closing(StringIO()) as s:
        for table_name in project.path_version.schema.tables:
            #path_table = path_tables[table_name]
            if not table_name in head_tables:
                if not table_name in project.path_version.migration.tables:
                    c = schema.CreateTableCommand()
                    c.table = table_name
                    project.path_version.migration.add_command(c)
                #s.write("create %s\n" % table_name)
        for table_name in project.head_version.schema.tables:
            if not table_name in path_tables:
                s.write('drop %s\n' % table_name)

#            head_table = head_tables[table_name]
#            if path_table != head_table:
#                # table already same as head
#                continue
#
#            if table_name in head_tables:
#                s.write(table_name + "\n")
        changes = s.getvalue()
#path.table != head.table
#if path.table in previous.tables
#    path.migrations.table.action = rename_table or alter_table
#if ! path.table in previous.tables
#    path.migraitons.table.action = create_table
#for table in pre
#if ! previous.table in path.tables
#    path.migrations.table.action = drop_table

    #path.table != head.table (also account for dropped tables head.table not in path.table)
    # Don't need this-??--and path.table not in path.migrations.tables

    # These are the changes that are in the path, but are NOT in the head.yml file
    # This includes changes to the path migration.yml file (for example a rename intead of drop/create
    if changes:
        with closing(StringIO()) as s:
            s.write('# Changed in directory but not added to sync:\n')
            s.write('#   (use "db add/drop/rename <table>..." to update what will sync)\n')
            s.write('#   (use "db undo <table>..." to undo change in directory)\n')
            s.write('#\n')
            s.write(changes)
            #s.write('# \033[31m{}\033[0m\n'.format('          new table:    test2'))
            return s.getvalue()


def _status_changes_in_database(project, s):
    #In the head.migrations and head.table != actual.table
    #[sync]  if actual.table = expected.table
    #[force] if actual.table != expected.table (will try to do what's right, but renamed columns are lost potentially)

    s.write('# Changed in database but not in project:\n')
    s.write('#   (use "db reverse [<table>...]" to save changes to directory)\n')
    s.write('#   (use "db sync --force [<table>]" to sync database to schema)\n')
    s.write('#\n')
    s.write('# \033[31m{}\033[0m\n'.format('          new table:    test1'))
    s.write('#\n')


#
#    def status2(self):
#        project.__ensure_valid()
#        db = database.get(project.connection_info)
#        head = version.get_previous(project.path)
#        db_schema = db.schema
#        yml_schema = project.__load_yml_schema()
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
#                cs.load(project.path + "/versions/head.yaml")
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


def main(argv=None):
    pass

if __name__ == "__main__":
    sys.exit(main())
