import inspect
import os
import pickle


def log(migration_object, message, data={}):
    factory_stack = _getLocals('createPloneObjects')['stack']
    migrator_locals = _getLocals('migrate')
    migrator = migrator_locals['self']
    migrator.log(migrator_locals, migration_object, message, factory_stack, data)


def logError(migration_object, message, data={}):
    factory_stack = _getLocals('createPloneObjects')['stack']
    migrator_locals = _getLocals('migrate')
    migrator = migrator_locals['self']
    migrator.logError(migrator_locals, migration_object, message, factory_stack, data)


def _getLocals(fun_name):
    stack = inspect.stack()
    locales = None
    for line in stack:
        if line[3] == fun_name:
            locales = line[0].f_locals
            break
    return locales


def picklesErrorLog(errors, filename='error_log.pickle', where='.'):
    current_directory = os.getcwd()
    os.chdir(where)
    i = 1
    new_filename = filename
    while filename in os.listdir('.'):
        i = i + 1
        new_filename = '%s - %i' % (filename, i)
    errors_export = open(new_filename, 'w')
    os.chdir(current_directory)
    pickle.dump(errors, errors_export)
    print 'error log "%s" pickled in : %s' % (new_filename, os.getcwd())
    return new_filename
