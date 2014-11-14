# -*- coding: utf-8 -*-

from imio.urban.dataimport.config import PRESERVE, OVERRIDE
from imio.urban.dataimport.errors import IdentifierError
from imio.urban.dataimport.errors import FactoryArgumentsError
from imio.urban.dataimport.interfaces import IUrbanDataImporter, IObjectsMapping,\
    IUrbanImportSource, IValuesMapping, IPostCreationMapper, IImportErrorMessage, \
    IFinalMapper

from plone import api

from zope.interface import implements

import zope
import transaction

import os
import pickle


class UrbanDataImporter(object):
    """
    """

    implements(IUrbanDataImporter)

    def __init__(self):
        """ """

        self.datasource = None
        self.objects_mappings = None
        self.values_mappings = None
        self.mode = PRESERVE
        self.savepoint_length = 0
        self.error_log_name = 'urban_dataimport'

        # attributes to be set up before running import
        self.factories = {}
        self.mappers = {}
        self.allowed_containers = {}

        # log and tracing vars
        self.current_line = 1
        self.current_containers_stack = []
        self.processed_lines = 0
        self.errors = {}
        self.sorted_errors = {}

    def setSavePoint(self, length):
        self.savepoint_length = length

    def importData(self, start=1, end=0):
        """ import data from line 'start' to line 'end' """

        self.setupImport()
        savepoint = self.savepoint_length
        processed_lines = 0

        for dataline in self.datasource.iterdata():
            if end and self.current_line > end:
                break
            elif start <= self.current_line:
                self.importDataLine(dataline)

                # save the import work every Nth line processed by commiting a transaction
                processed_lines += 1
                if savepoint and self.processed_lines % savepoint == 0:
                    transaction.commit()

            self.current_line += 1

    def importDataLine(self, dataline):
        print "PROCESSING LINE %i" % self.current_line
        objects_nesting = self.objects_mappings.getObjectsNesting()
        self.importGroupOfObjects(objects_nesting, dataline)

    def setupImport(self):

        self.datasource = zope.component.getAdapter(self, IUrbanImportSource, 'data source')
        self.objects_mappings = zope.component.getAdapter(self, IObjectsMapping, 'objects mapping')
        self.values_mappings = zope.component.getAdapter(self, IValuesMapping, 'values mapping')

        fields_mappings = self.objects_mappings.getRegisteredFieldsMapping()

        for objectname, mapping in fields_mappings.iteritems():
            self.setupFactory(objectname, mapping)
            self.setupObjectMappers(objectname, mapping)
            self.setupAllowedContainer(objectname, mapping)

    def setupFactory(self, objectname, mapping):
        factory_settings = mapping['factory']
        factory_class = factory_settings[0]
        factory_args = {}
        if len(factory_settings) == 2:
            factory_args = factory_settings[1]
        factory = factory_class(self, **factory_args)
        self.factories[objectname] = factory

    def setupObjectMappers(self, objectname, mapping):
        mappers = {
            'pre': [],
            'post': [],
            'final': [],
        }

        for mapper_class, mapper_args in mapping['mappers'].iteritems():
            #initialize the mapper
            mapper = mapper_class(self, mapper_args)
            if IPostCreationMapper.implementedBy(mapper_class):
                mappers['post'].append(mapper)
            elif IFinalMapper.implementedBy(mapper_class):
                mappers['final'].append(mapper)
            else:
                mappers['pre'].append(mapper)

        self.mappers[objectname] = mappers

    def setupAllowedContainer(self, objectname, mapping):
        allowed_containers = mapping.get('allowed_containers', None)
        if allowed_containers:
            self.allowed_containers[objectname] = allowed_containers

    def importGroupOfObjects(self, node, line):

        for object_name, subobjects in node:
            stack = []
            self.recursiveImportObjects(object_name, subobjects, line, stack)

        # once a full group of objects has been imported, we can store errors in
        # a simplified string  format
        if self.current_line in self.errors:
            line_num = self.current_line
            self.errors[line_num] = [str(error) for error in self.errors[line_num]]

    def recursiveImportObjects(self, object_name, childs, line, stack):

        self.current_containers_stack = stack

        factory_args = self.getFactoryArguments(line, object_name)
        multiple_factory_args = self.getMultipleFactoryArguments(line, object_name)

        if multiple_factory_args is not None and not factory_args:
            for args in multiple_factory_args:
                self.recursiveImportOneObject(object_name, childs, line, stack, args)
        elif factory_args and multiple_factory_args is None:
            self.recursiveImportOneObject(object_name, childs, line, stack, factory_args)
        else:
            raise FactoryArgumentsError

    def recursiveImportOneObject(self, object_name, childs, line, stack, factory_args):

        factory = self.factories[object_name]
        container = stack and stack[-1] or factory.getCreationPlace(factory_args)

        if not self.isAllowedType(object_name, container):
            return

        old_object = factory.objectAlreadyExists(factory_args, container)

        if old_object:
            if self.importer.mode == PRESERVE:
                urban_object = old_object

            elif self.importer.mode == OVERRIDE:
                api.content.delete(old_object)
                urban_object = factory.create(factory_args, container=container, line=line)

        else:
            urban_object = factory.create(factory_args, container=container, line=line)

        # if for some reasons the object creation went wrong, we skip this data line
        if urban_object is None:
            return

        # update some fields after creation but before child objects creation
        if self.mode != PRESERVE:
            self.updateObjectFields(line, object_name, urban_object, 'post')

        stack.append(urban_object)
        # recursive call
        for name, subobjects in childs:
            self.recursiveImportObjects(name, subobjects, line, stack)
        stack.pop()

        # update some fields after every child object has been created
        if self.mode != PRESERVE:
            self.updateObjectFields(line, object_name, urban_object, 'final')

        urban_object.processForm()

    def isAllowedType(self, object_name, container):
        if not container:
            return True

        portal_type = container.portal_type

        unrestricted_container = object_name not in self.allowed_containers
        allowed_container = portal_type in self.allowed_containers.get(object_name, '')

        allowed = unrestricted_container or allowed_container

        return allowed

    def getFactoryArguments(self, line, object_name):
        factory_args = {}
        for mapper in self.mappers[object_name]['pre']:
            args = mapper.map(line)
            if type(args) is not list:
                factory_args.update(args)

        return factory_args

    def getMultipleFactoryArguments(self, line, object_name):
        for mapper in self.mappers[object_name]['pre']:
            args = mapper.map(line)
            if type(args) is list:
                return args

    def updateObjectFields(self, line, object_name, urban_object, mapper_type):
        for mapper in self.mappers[object_name][mapper_type]:
            mapper.map(line, plone_object=urban_object)

    def logError(self, error_location, line, message, data):

        error = zope.component.getMultiAdapter((self, error_location, line, message, data), IImportErrorMessage)
        message = str(error)
        print message

        line_num = self.current_line
        if line_num not in self.errors:
            self.errors[line_num] = []
        self.errors[line_num].append(error)

        migration_step = error_location.__class__.__name__
        if migration_step not in self.sorted_errors:
            self.sorted_errors[migration_step] = []
        self.sorted_errors[migration_step].append(str(error))

    def log(self, migrator_locals, location, message, factory_stack, data):
        pass

    def picklesErrorLog(self, filename='', where='.'):
        if not filename:
            filename = '{}-errors-log.pickle'.format(self.error_log_name)

        current_directory = os.getcwd()
        os.chdir(where)

        i = 1
        new_filename = filename
        while new_filename in os.listdir('.'):
            i = i + 1
            new_filename = '%s - %i' % (filename, i)

        errors_export = open(new_filename, 'w')

        errors = dict([(k, v) for k, v in self.errors.iteritems()])
        sorted_errors = dict([(k, v) for k, v in self.sorted_errors.iteritems()])

        os.chdir(current_directory)
        all_errors = {
            'by_line': errors,
            'by_type': sorted_errors,
        }
        pickle.dump(all_errors, errors_export)

        print 'error log "%s" pickled in : %s' % (new_filename, os.getcwd())

        return new_filename
